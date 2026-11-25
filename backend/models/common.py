from typing import Literal

from pydantic import BaseModel

SourceType = Literal["MANGADEX", "ATHREA"]

TitleStatus = Literal["ONGOING", "COMPLETED", "HIATUS", "CANCELED"]


class StandardizedSource(BaseModel):
    name: str
    cover_url: str | None
    source_id: str
    source_type: SourceType
