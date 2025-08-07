import pytest

from src.main import hello


@pytest.mark.asyncio
async def test_hello():
  assert await hello("World") == "Hello, World!"
