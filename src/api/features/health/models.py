from pydantic import BaseModel


class HealthRequest(BaseModel):
  """
  Model for health check request.
  Currently, no specific fields are required.
  """

  pass


class HealthResponse(BaseModel):
  """
  Model for health check response.
  Contains a status field indicating the health status.
  """

  status: str
  message: str
