from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello(name: str = "World"):
  return f"Hello, {name}!"
