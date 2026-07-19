from __future__ import annotations

from pywarden.items import Item
from ..service import Service


class ItemsService(Service):
    def getAll(self) -> list[Item]:
        r = self.conn.get("/list/object/items")
        items = r.json()["data"]["data"]
        for item in items:
            fix_item(item)
        return items

    def deleteItem(self, id: str) -> None:
        self.conn.delete(f"/object/item/{id}")

    def getItem(self, id: str) -> Item:
        r = self.conn.get(f"/object/item/{id}")
        item = r.json()["data"]
        fix_item(item)
        return item


def fix_item(item):
    # ensure that attachments key is always set
    if "attachments" not in item:
        item["attachments"] = []
