import logging

from .enrollment_enums import SocialPlatform
from .scheduling import Scheduling
from .social import Social
from .generator import Generator
from .end_points import EndPoints
from .social_enrollment import SocialEnrollment
from .utility import to_supported_platforms


class SocialPosterWithGeneratedImage:
    def __init__(self, api_key):
        function = '(aloha) SocialPosterWithGeneratedImage.__init__'
        self.end_points = EndPoints.from_api_key(api_key)

        if not self.end_points:
            logging.error(f"{function} No endpoints available, unable to create instance")
            return

        self.generator = Generator(self.end_points, api_key)
        self.scheduling = Scheduling(self.generator)
        self.social = Social(self.end_points, api_key)


    def execute_for_client(self, social_enrollment: SocialEnrollment) -> bool:
        function = '(aloha) SocialPosterWithGeneratedImage:execute_for_client'
        client_id = ''
        try:
            if social_enrollment is None:
                raise TypeError('Missing social_enrollment')
            if social_enrollment.image_template_id is None:
                raise TypeError('Missing image_template_Id')

            client_id = social_enrollment.client_id
            if not self.scheduling.is_scheduled(
                client_id=client_id,
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

            supported_platforms = to_supported_platforms(text_dictionary,'scenario')

            if not supported_platforms:
                logging.warning(f'{function} no platforms found for client_id: {client_id} \n'
                                f' enrollment_Id: {social_enrollment.enrollment_id}')
                return True

            success = True
            for platform in supported_platforms:
                page = social_enrollment.to_page(platform)
                image_template_id = social_enrollment.image_template_id
                if not self.post_to_social(client_id, image_template_id, text_dictionary, platform, page):
                    success = False

            return success
        except Exception as error:
            logging.exception(f'{function}: failed to post to socials for client_id: {client_id} \n'
                                f' enrollment_id: {social_enrollment.enrollment_id} \n'
                                f' {error}')
            return False

    def post_to_social(self,
                       client_id: str,
                       image_template_id,
                       text_dictionary: dict,
                       platform: SocialPlatform,
                       page: str = None) -> bool:
        function = '(aloha) SocialPosterWithGeneratedImage:post_to_social'
        try:
            if platform == SocialPlatform.Facebook and (page is None):
                logging.warning(f'{function} Unable to post to facebook without a specified page for client_id: {client_id}')
                return False

            platform_name = platform.name.lower()
            social_text = None
            social_text_key = f'{platform_name}_text'
            social_scenario_key = f'{platform_name}_scenario'

            if social_text_key in text_dictionary:
                social_text = text_dictionary[social_text_key]

            merge_fields = None
            if social_scenario_key in text_dictionary:
                social_scenario = text_dictionary[social_scenario_key]
                merge_fields = {"image_scenario": social_scenario}

            image_url = self.generator.generate_image(
                client_id=client_id,
                template_id=image_template_id,
                merge_fields=merge_fields)

            if self.social.post_image(client_id, image_url, social_text, platform, page):
                logging.info(f'{function}: {platform}: Posted {image_url} for {client_id}')
                return True
            else:
                logging.error(f'{function}: {platform}: Unable to post for client_id {client_id} \n'
                              f' image_url: {image_url} \n'
                              f' page: {page} \n')
                return False
        except:
            logging.exception(f'{function}: {platform}: failed to post for {client_id}')
            return False



