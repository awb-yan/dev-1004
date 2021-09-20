import json
import requests
from odoo import exceptions
import logging

_logger = logging.getLogger(__name__)

class SalesforceAPIGatewayAuth(object):
    def __init__(
        self,
        url
    ):

        self.url = url


    def authenticate(
        self,
        client_id=None,
        client_secret=None,
        username=None,
        password=None):
        
        params = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }

        try: 
            res = requests.post(
                url = self.url,
                params = params
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)
        
        response = res.json()
        _logger.info(f'SF Authentication Response: {response}')

        token = response['access_token']

        return token
