import logging

from typing import List

from .enrollment_enums import SocialPlatform
from .image_gallery import ImageGallery
from .scheduling import Scheduling
from .social import Social
from .generator import Generator
from .end_points import EndPoints
from .social_enrollment import SocialEnrollment
from .utility import to_supported_platforms


class SocialPosterWithGalleryImage:
    def __init__(self, api_key):
        self.end_points = EndPoints.from_api_key(api_key)

        if not self.end_points:
            logging.error("No endpoints available, unable to create Scenario feeder")
            return

        self.generator = Generator(self.end_points, api_key)
        self.scheduling = Scheduling(self.generator)
        self.social = Social(self.end_points, api_key)
        self.image_gallery = ImageGallery(self.end_points, api_key)

    def execute_for_client(self,
                           social_enrollment: SocialEnrollment) -> bool:
        function = '(aloha) SocialPosterWithGalleryImage:execute_for_client'
        client_id = ''
        try:
            if social_enrollment is None:
                raise TypeError('Missing social_enrollment')

            client_id = social_enrollment.client_id
            if not self.scheduling.is_scheduled(
                client_id=social_enrollment.client_id,
                template_id=social_enrollment.scheduling_template_id):
                logging.info(f'{function}: skipping, not scheduled for this time for client_id: {client_id} \n'
                             f' scheduling_template_id: {social_enrollment.scheduling_template_id} \n'
                             f' enrollment_id: {social_enrollment.enrollment_id}')
                return True

            text_dictionary = self.generator.generate_text_to_object(
                client_id=client_id,
                template_id=social_enrollment.text_template_id)

            if not text_dictionary:
                logging.warning(f'{function}: skipping, no text generated for client_id: {client_id} \n'
                                f' text_template_id: {social_enrollment.text_template_id} \n'
                                f' enrollment_id: {social_enrollment.enrollment_id}')
                return False

            supported_platforms = to_supported_platforms(text_dictionary, 'text')
            if not supported_platforms:
                logging.warning(f'{function} no platforms found for client_id: {client_id} \n'
                                f' enrollment_Id: {social_enrollment.enrollment_id}')
                return True

            success = True
            for platform in supported_platforms:
                page = social_enrollment.to_page(platform)
                if not self.post_to_social(client_id, text_dictionary, platform, page):
                    success = False

            return success
        except Exception as error:
            logging.exception(f'{function} failed to post to socials for {client_id} \n{error}')
            return False

    def post_to_social(self,
                       client_id: str,
                       text_dictionary: dict,
                       platform: SocialPlatform,
                       page: str = None) -> bool:
        function = '(aloha) SocialPosterWithGalleryImage:post_to_social'
        try:
            if platform == SocialPlatform.Facebook and (page is None):
                logging.warning(f'{function} Unable to post to facebook without a specified page')
                return False

            platform_name = platform.name.lower()
            social_text = None
            social_text_key = f'{platform_name}_text'
            if social_text_key in text_dictionary:
                social_text = text_dictionary[social_text_key]

            image_url = self.image_gallery.get_random_image(client_id=client_id)
            if not image_url:
                logging.warning(f'{function}: {platform}: Unable to get image from gallery for {client_id}')
                return False

            if self.social.post_image(client_id, image_url, social_text, platform, page):
                logging.info(f'{function}: {platform}: Posted {image_url} for {client_id}')
                return True
            else:
                logging.error(f'{function}: {platform}: Unable to post {image_url} for {client_id}')
                return False
        except Exception as error:
            logging.exception(f'{function}:  {platform}: failed to post for {client_id} \n{error}')
            return False


