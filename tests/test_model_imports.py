def test_model_registry_imports_without_missing_modules() -> None:
    """Alembic imports this registry before every migration and deployment start."""
    import kall.models  # noqa: F401
