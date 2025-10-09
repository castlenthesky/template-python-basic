import pytest

from src.api.server import hello


@pytest.mark.asyncio
async def test_hello_strings():
  assert await hello("World") == "Hello, World!"
  assert await hello("Dagster") == "Hello, Dagster!"


@pytest.mark.asyncio
async def test_hello_empty():
  assert await hello("") == "Hello, !"
  # None should not be allowed as an input, will fall back to default "World"
  assert await hello(None) == "Hello, None!"
