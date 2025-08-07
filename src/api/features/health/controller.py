from src.api.features.health.models import HealthResponse

from . import service


async def handle_health_check() -> HealthResponse:
  user_input = service.validate_user_input()
  result = service.perform_health_check(user_input)
  return result
