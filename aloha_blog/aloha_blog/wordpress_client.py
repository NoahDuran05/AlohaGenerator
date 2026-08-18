#!/usr/bin/env python3
"""
Small WordPress.com client using an Application Password.

Usage:
 - pip install requests python-dotenv
 - Create a .env file (example provided)
 - Run: python wp_com_client.py

This script shows:
 - creating a draft post
 - uploading media and using it as featured image
 - creating categories if needed
"""
import os
import tempfile

from typing import List
from typing import Any
from urllib.parse import urlparse, unquote

import requests
from pydantic import BaseModel, ValidationError, TypeAdapter, model_validator
from requests.auth import HTTPBasicAuth

from .blog_post import BlogEntry, BlogMedia, BlogPostResult


class WordPressCategory(BaseModel):
    id: int
    name: str

    @classmethod
    def from_json_string(cls, json_string: str) -> List["WordPressCategory"]:
        adapter = TypeAdapter(list[cls])
        try:
            # validate directly from JSON string
            categories = adapter.validate_json(json_string)  # returns list[WordPressCategory]
            return categories
        except ValidationError as e:
            print("Validation error:", e)
            return []


class WordPressMedia(BaseModel):
    id: int
    source_url: str

    @classmethod
    def from_json_string(cls, json_string: str) -> "WordPressMedia | None":
        adapter = TypeAdapter(cls)
        try:
            # validate directly from JSON string
            media = adapter.validate_json(json_string)  # returns list[WordPressCategory]
            return media
        except ValidationError as e:
            print("Validation error:", e)
            return None

class WordPressElement(BaseModel):
    raw: str | None
    rendered: str | None

class WordPressPostResult(BaseModel):
    id: int
    status: str
    link: str
    content: WordPressElement | None
    title: WordPressElement | None

    @classmethod
    def from_json_string(cls, json_string: str) -> "WordPressPostResult | None":
        adapter = TypeAdapter(cls)
        try:
            # validate directly from JSON string
            media = adapter.validate_json(json_string)  # returns list[WordPressCategory]
            return media
        except ValidationError as e:
            print("Validation error:", e)
            return None


class WordPressEntry(BaseModel):
    title: str
    content: str
    status: str = "draft"
    categories: List[int] | None  = None
    tags: List[int] | None = None
    featured_media: int | None = None
    author: int | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": self.title,
            "content": self.content,
            "status": self.status,
        }
        if self.author:
            payload['author'] = self.author

        if self.categories:
            payload["categories"] = self.categories
        if self.tags:
            payload["tags"] = self.tags
        if self.featured_media:
            payload["featured_media"] = self.featured_media

        return payload

class WordPressConnection(BaseModel):
    username: str
    password: str
    website: str

    @model_validator(mode="after")
    def validate_model(self, model: "WordPressConnection") -> "WordPressConnection":
        if self.username is None:
            raise TypeError('Missing username')
        if self.password is None:
            raise TypeError('Missing password')
        if self.website is None:
            raise TypeError('Missing website')

        self.username = self.username.strip()
        self.password = self.password.strip()
        self.website = self.website.strip()
        return self

class WordPressClient:
    def __init__(self, connection: WordPressConnection, timeout: int = 20):
        self.site = connection.website
        self.auth = HTTPBasicAuth(connection.username, connection.password)
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"https://{self.site}/wp-json/wp/v2/{path.strip('/')}"



    def to_wordpress_blog_entry(self, blog_post: BlogEntry) -> WordPressEntry:
        wordpress_post = WordPressEntry(
            title=blog_post.title,
            content=blog_post.content,
            status=blog_post.status,
        )
        if blog_post.categories:
            wordpress_post.categories = self.category_names_to_ids(blog_post.categories)

        if blog_post.status.lower().startswith("publish"):
            wordpress_post.status = 'publish'

        if blog_post.author:
            wordpress_post.author = self.find_user_id_with_name_containing(blog_post.author)

        return wordpress_post

    def category_names_to_ids(self, names: List[str]) -> List[int]:
        id_list = []
        if not names:
            return id_list

        categories = self.get_categories()
        for name in names:
            if not name:
                continue
            for cat in categories:
                if not cat:
                    continue
                if not cat.name:
                    continue
                if cat.name.lower() == name.lower():
                    if not cat.id:
                        continue
                    if cat.id in id_list:
                        continue
                    id_list.append(cat.id)

        return id_list

    def post_blog_entry(self, blog_entry: BlogEntry, blog_media: BlogMedia | None) -> BlogPostResult | None:
        wp_entry = self.to_wordpress_blog_entry(blog_entry)

        if blog_media and blog_media.url:
            wp_media = self.upload_media(blog_media)
            if wp_media and wp_media.id:
                wp_entry.featured_media = wp_media.id
                #image_block = self.build_image_block(wp_media)
                #if image_block:
                #   wp_entry.content = f'{wp_entry.content}\n{image_block}'

        result =  self.post_wp_entry(wp_entry)
        if not result:
            return None

        blog_post_result = BlogPostResult(
            url = result.link,
            title = result.title.raw,
            status = result.status
        )
        return blog_post_result

    def post_wp_entry(self, post: WordPressEntry) -> WordPressPostResult:
        payload = post.to_payload()
        url = self._url('posts')
        resp = requests.post(url, json=payload, auth=self.auth, timeout=self.timeout)
        resp.raise_for_status()
        json_string = resp.text
        result = WordPressPostResult.from_json_string(json_string)
        print(result)
        return result

    def upload_media(self, upload: BlogMedia) -> WordPressMedia | None:
        """
        Upload a media file. Returns the media JSON (contains 'id' and 'source_url').
        WordPress.com accepts a multipart file upload to the /media endpoint.
        """
        if not upload:
            return None
        if not upload.url:
            return None

        tmp_filename = WordPressClient.download_to_temp(upload.url)
        headers = {"Content-Disposition": f'attachment; filename="{tmp_filename}"'}
        with open(tmp_filename, "rb") as f:
            files = {"file": (tmp_filename, f)}
            resp = requests.post(self._url("media"), headers=headers, files=files, auth=self.auth, timeout=60)
        resp.raise_for_status()
        json_text = resp.text
        media = WordPressMedia.from_json_string(json_text)

        # Optionally set title/caption after upload
        update = {}
        if upload.title:
            update["title"] = upload.title
        if upload.caption:
            update["caption"] = upload.caption
        if update:
            resp2 = requests.post(self._url(f"media/{media.id}"), json=update, auth=self.auth, timeout=self.timeout)
            resp2.raise_for_status()
            json_text = resp2.text
            media = WordPressMedia.from_json_string(json_text)

        os.remove(tmp_filename)
        return media

    def get_categories(self, per_page: int = 100) -> List[WordPressCategory]:
        resp = requests.get(self._url(f"categories?per_page={per_page}"), auth=self.auth, timeout=self.timeout)
        resp.raise_for_status()
        json_text = resp.text
        categories = WordPressCategory.from_json_string(json_text)
        return categories

    def create_category(self, name: str, slug: str = None, description: str = None):
        payload = {"name": name}
        if slug:
            payload["slug"] = slug
        if description:
            payload["description"] = description
        resp = requests.post(self._url("categories"), json=payload, auth=self.auth, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _get_users(self, per_page: int = 100) -> List[dict]:
        """Get list of users on the WordPress site"""
        resp = requests.get(self._url(f"users?per_page={per_page}"), auth=self.auth, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def find_user_id_with_name_containing(self, search: str) -> int | None:
        """Get a user by username"""
        if not search:
            return None
        search = search.lower().strip()
        users = self._get_users()
        found = None
        for user in users:
            slug = user.get('slug')
            name = user.get('name')
            if name:
                name = name.lower()

                if search in name:
                    found = user
                    break
            if slug:
                slug = slug.lower()
                if search in slug:
                    found = user
                    break

        if not found:
            return  None

        user_id = found.get('id')
        return user_id

    @staticmethod
    def download_to_temp(url: str) -> str | None:
        if not url:
            return None

        path = urlparse(url).path  # -> "/dir/image.jpg"
        path = unquote(path)  # decode %20 etc, if needed
        suffix = os.path.splitext(path)[1]

        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            # Keep delete=False if you want to reopen the file after closing.
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                return tmp.name

    @staticmethod
    def build_image_block(media: WordPressMedia, alt: str = "", caption: str = None) -> str:
        """
        Build HTML that embeds the image into the post content.
        We include the wp-image-{id} class when media_id is available so WP can recognize the attachment.
        The markup uses a figure block compatible with Gutenberg (works as plain HTML too).
        """
        class_attr = f' class="wp-image-{media.id}"' if media.id else ""
        alt_attr = f' alt="{alt}"' if alt else ' alt=""'
        caption_html = f'<figcaption class="wp-element-caption">{caption}</figcaption>' if caption else ""
        return f'<figure class="wp-block-image"><img src="{media.source_url}"{class_attr}{alt_attr}/>{caption_html}</figure>'

