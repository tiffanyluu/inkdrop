from typing import Literal

from pydantic import BaseModel

SourceType = Literal["MANGADEX", "ATHREA"]

TitleStatus = Literal["ONGOING", "COMPLETED", "HIATUS", "CANCELED"]


class TitleSource(BaseModel):
    source_id: str
    source_type: SourceType


class StandardizedSource(BaseModel):
    name: str
    cover_url: str | None
    authors: list[str] | None = None
    source_id: str
    source_type: SourceType
