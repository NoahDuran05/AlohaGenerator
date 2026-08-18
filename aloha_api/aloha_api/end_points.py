import logging

from .base_http import BaseHttp

class EndPoints:
    def __init__(self, content: str, generate: str, social: str):
        self.content = content
        self.generate = generate
        self.social = social


    @classmethod
    def from_api_key(cls, api_key: str):
        function = '(aloha) EndPoints:get_endpoints'
        try:
            if api_key is None or len(api_key) == 0:
                logging.error(f'{function} missing api_key')
                return None

            well_known_endpoint = "https://api.alohaagentics.org/configuration/internal-api-endpoints"
            response_json = BaseHttp.static_get_json(api_key, well_known_endpoint)
            return EndPoints.from_map(response_json)
        except:
            logging.error(f'{function} failed to get end points')

    @classmethod
    def from_map(cls, endpoint_map):
        content = endpoint_map.get("content")
        generate = endpoint_map.get("generate")
        social = endpoint_map.get("social")
        return EndPoints(content=content, generate=generate, social=social)




