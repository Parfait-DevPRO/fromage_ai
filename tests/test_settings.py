from config.settings import secret


def test_secret_reads_environment_variable(monkeypatch):
    monkeypatch.setenv("CHEESE_AI_TEST_KEY", "une-valeur-quelconque")
    assert secret("CHEESE_AI_TEST_KEY") == "une-valeur-quelconque"
