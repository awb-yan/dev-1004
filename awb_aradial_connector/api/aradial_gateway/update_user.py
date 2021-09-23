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
        _logger.info('function: update_user')

        try:
            res = requests.put(
                url=self.url+'/'+self.data['UserID'],
                headers=self.headers,
                data=json.dumps(self.data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        if res.status_code != 204:
            update_state = False
            _logger.error('!!! Error Updating Offer to '+self.data['Offer']+' for Subscriber '+self.data['UserID'])
        else:
            update_state = True

        return update_state