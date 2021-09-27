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
        balance_url,
        username,
        password,
        data
    ):

        self.url = url
        self.balance_url = balance_url
        self.username = username
        self.password = password

        self.headers = {
            'Content-Type': 'application/json'
        }

        self.data = data


    def update_user(self):
        _logger.info('function: update_user')

        update_state = True
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

        return update_state

    def update_timebank(self, UserID):
        _logger.info('function: update_timebank')
        _logger.info(self.data)

        update_state = True
        try:
            res = requests.post(
                url=self.balance_url+'/'+UserID,
                headers=self.headers,
                data=json.dumps(self.data),
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        if res.status_code != 201:
            update_state = False
            _logger.error('!!! Error Updating TimeBank to '+self.data['TimeBank']+' for Subscriber '+self.data['UserID'])

        return update_state
