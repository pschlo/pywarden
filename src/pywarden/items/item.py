from __future__ import annotations
from typing import TypedDict


class Item(TypedDict):
  id: str
  object: str
  organizationId: str
  collectionIds: list[str]
  folderId: str
  type: int
  name: str
  notes: str | None
  favorite: bool
  fields: list[Field]
  reprompt: int
  attachments: list[Attachment]

class Field(TypedDict):
  name: str
  value: str
  type: int

class Attachment(TypedDict):
  id: str
  fileName: str
  size: str
  sizeName: str
  url: str
