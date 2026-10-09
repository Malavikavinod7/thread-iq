import json
import sys
import time
from pathlib import Path

# Add project root to sys.path for clean imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.vision_agent import VisionAgent
from app.agents.description_agent import DescriptionAgent
from app.agents.validation_agent import ValidationAgent



def run_evaluation():
    dataset_path = Path(__file__).parent / "dataset.json"
    results_path = Path(__file__).parent / "results.md"

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    vision_agent = VisionAgent(ai_provider="local")
    desc_agent = DescriptionAgent(ai_provider="local")
    val_agent = ValidationAgent(ai_provider="local")

    total_samples = len(dataset)
    correct_category = 0
    correct_color = 0
    total_quality_score = 0.0
    total_time = 0.0

    eval_details = []

    for item in dataset:
        name = item["name"]
        exp_color = item["expected_color"]
        exp_cat = item["expected_category"]

        start_t = time.time()
        vis_res = vision_agent.analyze(product_name=name)
        desc_res = desc_agent.generate(product_name=name, visual_data=vis_res)
        val_res = val_agent.validate(desc_res, visual_data=vis_res)
        elapsed = time.time() - start_t

        pred_color = vis_res.get("primary_color", "")
        pred_cat = vis_res.get("category", "")
        q_score = val_res.get("quality_score", 0.0)

        # Check color match
        color_match = exp_color.lower() in pred_color.lower() or pred_color.lower() in exp_color.lower()
        if color_match:
            correct_color += 1

        # Check category match
        cat_match = exp_cat.split("/")[0].strip().lower() in pred_cat.lower() or pred_cat.split("/")[0].strip().lower() in exp_cat.lower()
        if cat_match:
            correct_category += 1

        total_quality_score += q_score
        total_time += elapsed

        eval_details.append({
            "name": name,
            "expected_color": exp_color,
            "predicted_color": pred_color,
            "color_match": color_match,
            "expected_category": exp_cat,
            "predicted_category": pred_cat,
            "category_match": cat_match,
            "quality_score": q_score,
            "time_sec": round(elapsed, 4),
        })

    cat_accuracy = (correct_category / total_samples) * 100
    color_accuracy = (correct_color / total_samples) * 100
    avg_quality = total_quality_score / total_samples
    avg_time = (total_time / total_samples) * 1000  # in ms

    print(f"=== ThreadIQ Local AI Pipeline Evaluation ===")
    print(f"Total Evaluated Samples: {total_samples}")
    print(f"Category Classification Accuracy: {cat_accuracy:.2f}% ({correct_category}/{total_samples})")
    print(f"Color Extraction Accuracy:    {color_accuracy:.2f}% ({correct_color}/{total_samples})")
    print(f"Average Quality Score:         {avg_quality:.2f} / 1.00")
    print(f"Average Latency per Product:   {avg_time:.2f} ms")

    markdown_report = f"""# ThreadIQ Local AI Pipeline Evaluation Report

## Benchmark Summary

| Metric | Value |
| --- | --- |
| **Total Test Samples** | {total_samples} |
| **Category Classification Accuracy** | **{cat_accuracy:.2f}%** ({correct_category}/{total_samples}) |
| **Color Extraction Accuracy** | **{color_accuracy:.2f}%** ({correct_color}/{total_samples}) |
| **Average Metadata Quality Score** | **{avg_quality:.2f} / 1.00** |
| **Average Latency per Item** | **{avg_time:.2f} ms** |

> **Note**: Evaluated using ThreadIQ's local deterministic heuristic intelligence engine on hand-labeled sample dataset (`eval/dataset.json`).

## Sample Breakdown

| Product Input Name | Exp Color / Pred Color | Exp Category / Pred Category | Quality Score | Latency |
| --- | --- | --- | --- | --- |
"""
    for d in eval_details:
        c_status = "✅" if d["color_match"] else "❌"
        cat_status = "✅" if d["category_match"] else "❌"
        markdown_report += f"| {d['name']} | {c_status} {d['predicted_color']} | {cat_status} {d['predicted_category']} | {d['quality_score']:.2f} | {d['time_sec']*1000:.1f}ms |\n"

    with open(results_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print(f"\nSaved evaluation report to {results_path}")


if __name__ == "__main__":
    run_evaluation()
