import logging

from .base_http import BaseHttp
from .end_points import EndPoints


class ImageGallery(BaseHttp):
    def __init__(self, end_points: EndPoints, api_key: str):
        super().__init__(api_key)
        self.end_points = end_points

    @classmethod
    def from_api_key(cls, api_key: str):
        end_points = EndPoints.from_api_key(api_key)
        return cls(end_points, api_key)

    def get_random_image(self, client_id: str) -> str | None:
        function = '(aloha) ImageGallery:get_random_image'
        try:
            url = self.end_points.content + f'/api/random-image?code=aloha&client={client_id}'
            result = self._get_json(url)
            if result is None:
                return None
            return result.get("value")
        except:
            logging.exception(f'{function}: failed to get random image for {client_id}')
            return None
