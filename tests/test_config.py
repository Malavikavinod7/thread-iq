import importlib


def test_settings_read_environment_values(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "ThreadIQ")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/threadiq")
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "true")

    import app.core.config as config_module

    config_module = importlib.reload(config_module)

    assert config_module.settings.project_name == "ThreadIQ"
    assert config_module.settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/threadiq"
    assert config_module.settings.environment == "testing"
    assert config_module.settings.debug is True
