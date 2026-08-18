from typing import List

from pydantic import BaseModel


class BlogEntry(BaseModel):
    title: str
    content: str
    status: str = "draft"
    categories: List[str] = None
    tags: List[str] = None
    author: str | None = None


class BlogMedia(BaseModel):
    url: str
    title: str = None,
    caption: str = None

class BlogPostResult(BaseModel):
    url: str
    title: str
    status: str = "draft"
