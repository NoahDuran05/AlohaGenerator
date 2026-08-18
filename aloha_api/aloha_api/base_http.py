import requests
import logging

class BaseHttp:
    def __init__(self, api_key):
        function = '(aloha) BaseHttp.__init__'

        self.api_key = api_key

        if not api_key:
            logging.error(f'{function} missing api_key')
            raise ValueError('missing api key')


    def _get_json(self, url: str):
        function = '(aloha) BaseHttp:get_json'
        try:
            return self.static_get_json(self.api_key, url)
        except:
            logging.exception(f'{function} failed to get json \n '
                              f' for url: {url}')

    def _post_json(self, url: str, request_dict: dict):
        function = '(aloha) BaseHttp:post_json'
        headers = {
            "X-Api-Key": self.api_key
        }
        try:
            response = requests.post(url, headers=headers, json=request_dict)
            if response.status_code == 200:
                response_json = response.json()
                return response_json
            else:
                logging.warning(f"{function}: error: {response.status_code} - {response.text} \n"
                                f' for url: {url}')
            return None
        except:
            logging.exception(f'{function} failed to post to {url}')
            return None

    def _post(self, url: str, request_dict: dict) -> bool:
        function = '(aloha) BaseHttp:_post'
        headers = {
            "X-Api-Key": self.api_key
        }
        try:
            response = requests.post(url, headers=headers, json=request_dict)
            if response.status_code == 200:
                return True
            else:
                logging.warning(f"{function}: error: {response.status_code} - {response.text} \n "
                                f' for url: {url}')
            return False
        except:
            logging.exception(f'{function} failed to post to {url}')
            return False

    @classmethod
    def static_get_json(cls, api_key: str, url: str):
        function = '(aloha) BaseHttp:static_get_json'
        headers = {
            "X-Api-Key": api_key
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_response = response.json()
                return json_response
            else:
                print(f"{function}: error: {response.status_code} - {response.text} \n "
                      f' for url: {url}')
            return None
        except:
            logging.exception(f'{function} failed to get with {url}')
            return None

