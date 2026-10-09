import uuid
import pytest
from app.agents.base import BaseAgent
from app.agents.description_agent import DescriptionAgent
from app.agents.embedding_agent import EmbeddingAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.vision_agent import VisionAgent
from app.core.enums import JobStatus
from app.models.job import Job
from app.repositories.job_repository import InMemoryJobRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.job_service import JobService


def test_base_agent_provider_resolution():
    agent = BaseAgent(ai_provider="auto", openai_api_key=None, gemini_api_key=None)
    assert agent.get_active_provider() == "local"

    agent_openai = BaseAgent(ai_provider="openai", openai_api_key="sk-fake-key")
    assert agent_openai.get_active_provider() == "openai"

    agent_gemini = BaseAgent(ai_provider="gemini", gemini_api_key="fake-gemini-key")
    assert agent_gemini.get_active_provider() == "gemini"


def test_vision_agent_analyzes_fashion_item():
    vision_agent = VisionAgent(ai_provider="local")
    res = vision_agent.analyze(product_name="Navy Blue Slim Denim Shirt")

    assert res["primary_color"] == "Navy Blue"
    assert res["material_look"] == "Cotton / Denim"
    assert res["fit_style"] == "Slim Fit"
    assert res["category"] == "Apparel / Tops"
    assert res["confidence_score"] > 0.8
    assert res["provider_used"] == "local"


def test_description_agent_generates_copy_and_tags():
    desc_agent = DescriptionAgent(ai_provider="local")
    visual_data = {
        "primary_color": "Crimson Red",
        "pattern": "Solid",
        "material_look": "Silk / Satin",
        "category": "Apparel / Dresses",
        "fit_style": "Regular Fit",
    }
    res = desc_agent.generate(product_name="Party Evening Dress", visual_data=visual_data)

    assert "Crimson Red" in res["title"]
    assert "party evening dress" in res["title"].lower()
    assert len(res["description"]) > 20
    assert len(res["key_features"]) >= 3
    assert "fashion" in res["tags"]
    assert res["provider_used"] == "local"


def test_validation_agent_audits_valid_and_invalid_metadata():
    val_agent = ValidationAgent(ai_provider="local")

    valid_desc = {
        "title": "Classic Black Leather Jacket",
        "description": "Premium genuine leather biker jacket designed for comfort and modern style.",
        "tags": ["black", "leather", "jacket", "fashion"],
    }
    valid_result = val_agent.validate(valid_desc, visual_data={"primary_color": "Black"})
    assert valid_result["is_valid"] is True
    assert valid_result["quality_score"] >= 0.9
    assert valid_result["passed_safety_checks"] is True

    # Test short title error
    invalid_desc = {
        "title": "A",
        "description": "Short",
        "tags": [],
    }
    invalid_result = val_agent.validate(invalid_desc)
    assert invalid_result["is_valid"] is False
    assert any("< 2 chars" in err for err in invalid_result["errors"])

    # Test profanity failure
    profane_desc = {
        "title": "Fake Counterfeit Luxury Bag",
        "description": "Explicit scam product listing.",
        "tags": ["fake"],
    }
    profane_result = val_agent.validate(profane_desc)
    assert profane_result["is_valid"] is False
    assert profane_result["passed_safety_checks"] is False


def test_embedding_agent_generates_normalized_vector():
    embed_agent = EmbeddingAgent(ai_provider="local")
    res = embed_agent.embed("Navy Blue Denim Shirt for Men", dimension=128)

    assert len(res["vector"]) == 128
    assert res["dimension"] == 128
    assert res["provider_used"] == "local"
    # Verify vector normalization (L2 norm ~ 1.0)
    l2_norm = sum(x * x for x in res["vector"])
    assert pytest.approx(l2_norm, 0.01) == 1.0


def test_agent_orchestrator_executes_all_real_agents():
    job_repo = InMemoryJobRepository()
    job_service = JobService(job_repo)

    vision = VisionAgent(ai_provider="local")
    desc = DescriptionAgent(ai_provider="local")
    val = ValidationAgent(ai_provider="local")
    embed = EmbeddingAgent(ai_provider="local")

    orchestrator = AgentOrchestrator(
        job_service=job_service,
        vision_agent=vision,
        description_agent=desc,
        validation_agent=val,
        embedding_agent=embed,
    )

    job = Job(product_id=str(uuid.uuid4()), status=JobStatus.PENDING)
    created_job = job_service.create_job(job)

    result_job = orchestrator.run(created_job)

    assert result_job.status == JobStatus.COMPLETED
    assert result_job.current_step == "COMPLETED"
    assert result_job.started_at is not None
    assert result_job.finished_at is not None
    assert result_job.error_message is None


def test_vision_agent_accepts_image_url():
    vision = VisionAgent(ai_provider="local")
    result = vision.analyze(product_name="Silk Red Scarf", image_url="https://example.com/scarf.jpg")
    assert result["primary_color"] == "Crimson Red"
    assert result["material_look"] == "Silk / Satin"
    assert result["confidence_score"] > 0.0
