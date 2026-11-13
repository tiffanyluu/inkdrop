from datetime import datetime
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

    @property
    def display_description(self) -> str | None:
        if not self.description:
            return None
        elif "en" in self.description:
            return self.description["en"]
        else:
            return next(iter(self.description.values()))


class MangaRelationship(BaseModel):
    id: str
    type: str
    attributes: dict | None = None


class Manga(BaseModel):
    id: str
    attributes: MangaAttributes
    relationships: list[MangaRelationship]

    @property
    def cover_url(self) -> str | None:
        for relationship in self.relationships:
            if relationship.type == "cover_art":
                if relationship.attributes is None:
                    return None
                cover_filename = relationship.attributes["fileName"]
                return f"https://uploads.mangadex.org/covers/{self.id}/{cover_filename}"


class ChapterAttributes(BaseModel):
    chapter: str | None
    title: str | None
    external_url: str | None = Field(alias="externalUrl")
    readable_at: datetime | None = Field(alias="readableAt")


class Chapter(BaseModel):
    id: str
    attributes: ChapterAttributes


class ChapterFeed(BaseModel):
    data: list[Chapter]
    limit: int
    offset: int
    total: int

    @property
    def latest_free_chapter(self) -> Chapter | None:
        for chapter in self.data:
            if chapter.attributes.external_url is None:
                return chapter

        return None
