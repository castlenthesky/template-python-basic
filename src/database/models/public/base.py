"""Base table model with SQLModel."""

from typing import ClassVar

from sqlmodel import SQLModel


class ExampleBase(SQLModel, table=False):
  """Base table model."""

  __table_args__: ClassVar[dict] = {"schema": "public"}
