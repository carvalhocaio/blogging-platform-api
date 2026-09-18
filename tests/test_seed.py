from pathlib import Path

from blogging_platform_api.config import Settings, get_settings
from blogging_platform_api.infrastructure.persistence.database import create_engine
from blogging_platform_api.infrastructure.seed import seed


def test_default_settings_database_url_is_valid() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    assert engine.url.database == "dema.db"


async def test_seed_populates_database(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    settings = Settings(database_url=f"sqlite+aiosqlite:///{db_file}")
    created = await seed(settings)
    assert created == 5

    second_run = await seed(settings)
    assert second_run == 0
