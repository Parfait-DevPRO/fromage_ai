from config.settings import resolve_model_path


def test_model_resolver_returns_a_path():
    assert resolve_model_path().suffix in {".keras", ".h5"}
