import json
import logging

from .end_points import EndPoints
from .base_http import BaseHttp

class Generator(BaseHttp):
    def __init__(self, end_points: EndPoints, api_key: str):
        super().__init__(api_key)
        self.end_points = end_points

    @classmethod
    def from_api_key(cls, api_key: str):
        end_points = EndPoints.from_api_key(api_key)
        return cls(end_points, api_key)

    def generate_image(self, client_id: str, template_id: str, merge_fields: dict = None) -> str | None:
        function = '(aloha) Generator:generate_image'
        try:
            url = self.end_points.generate + '/api/generate-image?code=aloha'

            request_data = Generator.build_request(client_id, template_id, merge_fields)
            if not request_data:
                return None
            result = self._post_json(url, request_data)
            if result is None:
                return None
            return result.get("value")
        except:
            logging.exception(f'{function}: failed to generate image for client_id: {client_id}'
                              f' template_id: {template_id}')
            return None

    def generate_text(self, client_id: str, template_id: str, merge_fields: dict = None) -> str | None:
        function = '(aloha) Generator:generate_text'
        try:
            url = self.end_points.generate + '/api/generate-text?code=aloha'
            request_data = self.build_request(client_id, template_id, merge_fields)
            if not request_data:
                return None
            result = self._post_json(url, request_data)
            if result is None:
                return None
            return result.get("value")
        except:
            logging.exception(f'{function}: failed to generate text for client_id: {client_id}'
                              f' template_id: {template_id}')
            return None

    def generate_boolean(self, client_id: str, template_id: str, merge_fields: dict = None) -> bool | None:
        function = '(aloha) Generator:generate_boolean'
        try:
            url = self.end_points.generate + '/api/generate-boolean?code=aloha'
            request_data = self.build_request(client_id, template_id, merge_fields)
            if not request_data:
                return None
            result = self._post_json(url, request_data)
            if result is None:
                return None
            return result.get("value")
        except:
            logging.exception(f'{function}: failed to generate boolean for client_id: {client_id}'
                              f' template_id: {template_id}')
            return None

    def generate_text_to_object(self, client_id: str, template_id: str, merge_fields: dict | None = None) -> dict | None:
        function = '(aloha) Generator:generate_text_to_object'
        if client_id is None:
            raise TypeError('Missing client_id')
        if template_id is None:
            raise TypeError('Missing template_id')

        text = self.generate_text(client_id, template_id, merge_fields)
        if not text:
            return None
        json_string = Generator.strip_json_code_block(text)
        try:
            loaded = json.loads(json_string)
            return loaded
        except:
            logging.error(f'{function} failed to deserialize:\n {json_string}')
            return None

    def _post(self, url: str, request_data: dict):
        json_response = self._post_json(url, request_data)

        if json_response is None:
            return None

        return json_response.get("value")

    @staticmethod
    def build_request(client_id: str, template_id: str, merge_fields: dict=None) -> dict | None:
        function = '(aloha) Generator:build_request'
        try:
            request_data = dict()
            if client_id is None:
                raise TypeError("Missing client_id")
            request_data["clientId"] = client_id

            if template_id is None:
                raise TypeError("Missing template_id")
            request_data["templateId"] = template_id

            if merge_fields:
                request_data["mergeFields"] = merge_fields
            return request_data
        except:
            logging.exception(f'{function} failed to build request for {client_id} with {template_id} \n {merge_fields}')
            return None

    @staticmethod
    def strip_json_code_block(s: str) -> str:
        function = '(aloha) strip_json_code_block'
        try:
            start = "```json"
            end = "```"
            # Check for leading/trailing whitespace and process accordingly
            s = s.strip()
            index = s.find(start)
            if index > -1 and s.rstrip().endswith(end):
                # Remove starting '```json'
                s = s[index + len(start):]
                # Remove trailing '```'
                s = s.rstrip()
                s = s[:-len(end)]
                # Remove leading/trailing whitespace after strip
                return s.strip()

            if s.find('{') == 0 and s.endswith('}'):
                return s

            index = s.find('{')
            if index > 0 and s.endswith('}'):
                s = s[(index-1):]

            return s
        except:
            logging.exception(f'{function}: failed to extract json from: {s}')
            return s
