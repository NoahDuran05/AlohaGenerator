import logging

from pydantic import BaseModel, model_validator
from typing import List

from aloha_blog.blog_post import BlogEntry, BlogMedia, BlogPostResult
from aloha_blog.wordpress_client import WordPressClient, WordPressConnection
from .end_points import EndPoints
from .enrollments import Enrollments
from .generator import Generator
from .scheduling import Scheduling


class BlogPostRequest(BaseModel):
    author: str | None
    client_id: str
    scheduling_template_id: str
    text_template_id: str
    image_template_id: str | None
    image_url: str | None
    blog_entry_status: str | None

    @model_validator(mode="after")
    def validate_model(self, model: "BlogPostRequest") -> "BlogPostRequest":
        if self.image_url:
            if self.image_template_id:
                raise ValueError("image_url and image_template_id are mutually exclusive")

        if self.client_id is None:
            raise ValueError('Missing client_id')
        if self.scheduling_template_id is None:
            raise ValueError('Missing scheduling_template_id')
        if self.text_template_id is None:
            raise TypeError('Missing text_template_id')

        return self


class BlogPoster:
    def __init__(self, api_key):
        function = '(aloha) BlogPoster.__init__'
        self.end_points = EndPoints.from_api_key(api_key)

        if not self.end_points:
            message = "No endpoints available, unable to create instance"
            logging.error(f"{function}: {message}")
            raise Exception(message)

        self.enrollments = Enrollments(api_key)
        self.generator = Generator(self.end_points, api_key)
        self.scheduling = Scheduling(self.generator)

    def execute_for_enrollment(self,
                           enrollment_id: str
                           ) -> BlogPostResult | None :
        function = '(aloha) BlogPoster.execute_for_enrollment'
        try:
            enrollment = self.enrollments.get_enrollment_by_id(enrollment_id)
            if not enrollment:
                logging.warning(f'{function}: active enrollment not found for {enrollment_id}')
                return None

            request = BlogPostRequest(
                author=enrollment.get_author(),
                client_id=enrollment.get_client_id(),
                scheduling_template_id=enrollment.get_scheduling_template_id(),
                text_template_id=enrollment.get_text_template_id(),
                image_template_id=enrollment.get_image_template_id(),
                image_url=None,
                blog_entry_status=enrollment.get_blog_post_status()
            )
            connection = WordPressConnection(
                website=enrollment.get_website(),
                username=enrollment.get_username(),
                password=enrollment.get_password()
            )
            return self.execute(request, connection)
        except Exception as e:
            logging.exception(f'{function}: failed with {enrollment_id}\n{e}', stack_info=True)
            return None

    def execute(self,
                request: BlogPostRequest,
                connection: WordPressConnection
                ) -> BlogPostResult | None:
        function = '(aloha) BlogPosterWithGeneratedImage:execute_for_client'
        try:
            if not self.scheduling.is_scheduled(
                    client_id=request.client_id,
                    template_id=request.scheduling_template_id):
                logging.info(f'{function}: skipping, not scheduled for this time for client_id: {request.client_id} \n'
                             f' scheduling_template_id: {request.scheduling_template_id}')
                return None

            text_dictionary = self.generator.generate_text_to_object(
                client_id=request.client_id,
                template_id=request.text_template_id)

            blog_entry = BlogPoster._to_blog_entry(request, text_dictionary)
            if not blog_entry:
                logging.warning(f'{function}: unable to create blog entry, skipping for client_id: {request.client_id}'
                                f' text_template_id: {request.text_template_id}')
                return None

            image_url = self._get_image(request, text_dictionary)

            result = BlogPoster._post_blog_entry(connection, request.client_id, blog_entry, image_url)
            if not result:
                return None

            logging.info(f'{function}: posted to {result.url} for {request.client_id}')
            return result
        except Exception as e:
            logging.exception(f'{function}: failed to execute for client {request.client_id} \n {e}')
            return None

    @staticmethod
    def _to_blog_entry(request: BlogPostRequest, text_dictionary: dict) -> BlogEntry | None:
        function = "BlogPoster._to_blog_entry"

        if not text_dictionary:
            logging.warning(f'{function}: skipping, no text generated for client_id: {request.client_id} \n')
            return None

        blog_text_key = 'blog_text'
        if blog_text_key in text_dictionary:
            blog_text: str = text_dictionary[blog_text_key]
        else:
            logging.warning(f'{function} missing {blog_text_key} for client_id: {request.client_id}')
            return None

        blog_title_key = 'blog_title'
        if blog_title_key in text_dictionary:
            blog_title: str = text_dictionary[blog_title_key]
        else:
            logging.warning(f'{function} missing {blog_title_key} for client_id: {request.client_id}')
            return None

        blog_categories: List[str] = []
        blog_categories_key = 'blog_categories'
        if blog_categories_key in text_dictionary:
            blog_categories = text_dictionary[blog_categories_key]

        blog_entry = BlogEntry(
            content=blog_text,
            title=blog_title,
            categories=blog_categories,
        )
        if request.blog_entry_status:
            blog_entry = request.blog_entry_status
        if request.author:
            blog_entry.author = request.author

        return blog_entry

    def _get_image(self, request: BlogPostRequest, text_dictionary: dict) -> str | None:
        function = "(aloha) BlogPoster:get_image"
        if not request:
            return None
        if request.image_url:
            return request.image_url

        if not request.image_template_id:
            return None

        image_scenario_key = 'image_scenario'
        if not image_scenario_key in text_dictionary:
            logging.warning(f'{function} missing {image_scenario_key} for client_id: {request.client_id}')
            return None

        image_scenario = text_dictionary[image_scenario_key]
        merge_fields = {"image_scenario": image_scenario}
        image_url = self.generator.generate_image(
            client_id=request.client_id,
            template_id=request.image_template_id,
            merge_fields=merge_fields)
        return image_url


    @staticmethod
    def _post_blog_entry(connection: WordPressConnection, client_id: str,  blog_entry: BlogEntry, image_url: str | None) -> BlogPostResult | None:
        function = '(aloha) BlogPoster._post_blog_entry'
        try:
            wordpress_client = WordPressClient(connection)
            blog_media = None
            if image_url:
                blog_media = BlogMedia(
                    url=image_url
                )

            result = wordpress_client.post_blog_entry(blog_entry, blog_media)
            return result
        except Exception as e:
            logging.exception(f'{function} failed to execute for client_id: {client_id} \n {e}', stack_info=True)
            return None

