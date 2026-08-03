from kall.config import normalize_database_url


def test_normalizes_render_postgres_url_to_psycopg_v3() -> None:
    assert (
        normalize_database_url("postgres://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_normalizes_standard_postgresql_url_to_psycopg_v3() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


def test_preserves_explicit_driver_and_sqlite_urls() -> None:
    assert normalize_database_url("postgresql+psycopg://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )
    assert normalize_database_url("sqlite:///./kall.db") == "sqlite:///./kall.db"
