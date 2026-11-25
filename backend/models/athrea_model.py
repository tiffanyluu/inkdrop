from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AthreaSeries(BaseModel):
    name: str
    cover_url: str
    status: str
    description: str
    latest_free_chapter: Decimal | None
    latest_free_chapter_datetime: datetime | None
    latest_paid_chapter: Decimal | None
