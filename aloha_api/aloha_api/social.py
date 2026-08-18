import logging

from .base_http import BaseHttp
from .end_points import EndPoints
from .enrollment_enums import SocialPlatform


class Social(BaseHttp):
    def __init__(self, end_points: EndPoints, api_key: str):
        super().__init__(api_key)
        self.end_points = end_points

    @classmethod
    def from_api_key(cls, api_key: str):
        end_points = EndPoints.from_api_key(api_key)
        return cls(end_points, api_key)

    def post_image_to_instagram(self, client_id: str, image_url: str, text: str) -> bool:
        return self.post_image(client_id, image_url, text, SocialPlatform.Instagram)

    def post_image_to_facebook(self, client_id: str, image_url: str, text: str, page: str) -> bool:
        return self.post_image(client_id, image_url, text, SocialPlatform.Facebook, page)

    def post_image_to_linkedin(self, client_id: str, image_url: str, text: str) -> bool:
        return self.post_image(client_id, image_url, text, SocialPlatform.LinkedIn)

    def post_image(self, client_id: str, image_url: str, text: str, platform: SocialPlatform, page = None) -> bool:
        function = '(aloha) Social:post_image'
        if not client_id:
            logging.warning(f'{function}: called with null client_id')
            return False
        if not image_url:
            logging.info(f'{function} called with null image_url for {client_id} - {platform} ')
            return False
        if not platform:
            logging.warning(f'{function} called with null platform for {client_id}')
            return False
        if platform == SocialPlatform.Facebook and (page is None):
            logging.warning(f'{function} unable to post to {platform.name} without a specified page')
            return False

        try:
            url =  f'{self.end_points.social}/social-posting/{platform.name.lower()}/image'
            data = {
                "client": client_id,
                "image": image_url,
                "text": text
            }
            if page:
                data["page"] = page

            success  = self._post(url, data)
            return success
        except:
            logging.exception(f'{function}: failed to post for {client_id} to {platform}')
            return False

    def post_link_to_facebook(self, client_id: str, link_url: str, text: str, page: str) -> bool:
        return self.post_link(client_id, link_url, text, SocialPlatform.Facebook, page)

    def post_link_to_linkedin(self, client_id: str, link_url: str, text: str) -> bool:
        return self.post_link(client_id, link_url, text, SocialPlatform.LinkedIn)

    def post_link(self, client_id: str, link_url: str, text: str, platform: SocialPlatform, page = None) -> bool:
        function = '(aloha) Social:post_link'
        if not client_id:
            logging.warning(f'{function}: called with null client_id')
            return False
        if not link_url:
            logging.info(f'{function} called with null link_url for {client_id} - {platform} ')
            return False
        if not platform:
            logging.warning(f'{function} called with null platform for {client_id}')
            return False
        if platform == SocialPlatform.Facebook and (page is None):
            logging.warning(f'{function} unable to post to {platform.name} without a specified page')
            return False

        try:
            url =  f'{self.end_points.social}/social-posting/{platform.name.lower()}/link'
            data = {
                "client": client_id,
                "link": link_url,
                "text": text
            }
            if page:
                data["page"] = page

            success  = self._post(url, data)
            return success
        except:
            logging.exception(f'{function}: failed to post for {client_id} to {platform}')
            return False
