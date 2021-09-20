import json
import requests
from odoo import exceptions
from requests.auth import HTTPBasicAuth

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGatewayUpdateUser(object):
    def __init__(
        self,
        url,
        username,
        password,
        data
    ):

        self.url = url
        self.username = username
        self.password = password

        self.headers = {
            'Content-Type': 'application/json'
        }

        self.data = data


    def update_user(self):

        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        _logger.info(res.json())
        
        state = True if res.status_code == 201 else False
        _logger.info("response [%s]" % res)

        return state
