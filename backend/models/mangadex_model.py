from typing import Literal

from pydantic import BaseModel, Field


class MangaAttributes(BaseModel):
    title: dict[str, str]
    alt_titles: list[dict[str, str]] = Field(alias="altTitles")
    description: dict[str, str]
    status: Literal["ongoing", "completed", "hiatus", "cancelled"]

    @property
    def display_title(self) -> str:
        if "en" in self.title:
            return self.title["en"]

        for titles in self.alt_titles:
            if "en" in titles:
                return titles["en"]

        if "ja-ro" in self.title:
            return self.title["ja-ro"]
        else:
            return next(iter(self.title.values()))


class MangaRelationship(BaseModel):
    id: str
    type: str
    attributes: dict | None = None


class Manga(BaseModel):
    id: str
    attributes: MangaAttributes
    relationships: list[MangaRelationship]

    @property
    def cover_image_url(self) -> str | None:
        for relationship in self.relationships:
            if relationship.type == "cover_art":
                if relationship.attributes is None:
                    return None
                cover_filename = relationship.attributes["fileName"]
                return f"https://uploads.mangadex.org/covers/{self.id}/{cover_filename}"
