import pytest


@pytest.mark.asyncio
async def test_health_check():
  from src.api.features.health.service import perform_health_check, validate_user_input

  user_input = validate_user_input()
  result = perform_health_check(user_input)
  assert result.status == "healthy"
  assert result.message == "Service is running smoothly"


@pytest.mark.asyncio
async def test_health_check_invalid_input():
  from src.api.features.health.service import perform_health_check

  result = perform_health_check(False)
  assert result.status == "error"
  assert result.message == "Invalid input provided for health check"
