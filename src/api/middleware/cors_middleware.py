from fastapi.middleware.cors import CORSMiddleware


def configure_cors_middleware(app):
  """
  Configures CORS middleware for the FastAPI application.

  This function adds the CORSMiddleware to the FastAPI app, allowing cross-origin requests.
  Adjust the `allow_origins` parameter as needed for your application.
  """
  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
