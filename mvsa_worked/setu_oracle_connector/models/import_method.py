import requests
import re
from odoo.exceptions import ValidationError


# class GetToken:
    # def __init__(self, url, payload, headers):
    #     self.url = url
    #     self.payload = payload
    #     self.headers = headers
    #
    # def get_token(self):
    #     session = requests.Session()
    #     response = session.post(self.url + '/api/TokenAuth/Authenticate', json=self.payload, headers=self.headers)
    #     return response
    #
    # @staticmethod
    # def _is_valid_url(url):
    #     pattern = r'^(https?://)?[\w.-]+\.[a-zA-Z]{2,}(/.*)?$'
    #     return re.match(pattern, url) is not None
