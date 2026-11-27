from pydantic import BaseModel


class CoverResult(BaseModel):
    image_bytes: bytes
    content_type: str
