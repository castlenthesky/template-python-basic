import pytest


@pytest.mark.asyncio
async def test_health_check():
    from src.services.health.service import HealthService

    service = HealthService()
    user_input = service.validate_user_input()
    result = service.perform_health_check(user_input)
    assert result.status == "healthy"
    assert result.message == "Service is running smoothly"


@pytest.mark.asyncio
async def test_health_check_invalid_input():
    from src.services.health.service import HealthService

    service = HealthService()
    result = service.perform_health_check(False)
    assert result.status == "error"
    assert result.message == "Invalid input provided for health check"
