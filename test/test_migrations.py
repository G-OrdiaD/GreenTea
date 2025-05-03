import pytest
from alembic.command import upgrade, downgrade
from alembic.config import Config

@pytest.fixture
def alembic_config():
    return Config("migrations/alembic.ini")

def test_migrations_up_and_down(alembic_config):
    # Test full upgrade then downgrade
    upgrade(alembic_config, "head")
    downgrade(alembic_config, "base")
    upgrade(alembic_config, "head")  # Final re-upgrade