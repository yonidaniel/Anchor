from pydantic import BaseModel
from typing import Union


class SheetSchema(BaseModel):
    columns: list[dict[str, str]]


class CellValueSchema(BaseModel):
    value: Union[str, bool, int, float]
