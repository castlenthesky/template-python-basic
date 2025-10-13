from uuid import uuid4

USERS = [
  {"id": "7d2d7b03-5946-49a2-aebe-f0e8b964667d", "username": "alice"},
  {"id": "1adbadb9-5957-40b9-9c15-4af589a052bf", "username": "bob"},
  {"id": "c6fcd4e3-6097-44f0-91bb-af763410e8ba", "username": "charlie"},
]


if __name__ == "__main__":
  for i in range(10):
    print(uuid4())
