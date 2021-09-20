import json
import requests
from odoo import exceptions
import logging

_logger = logging.getLogger(__name__)

class SalesforceAPIGatewayUpdateAccount(object):
    def __init__(
        self,
        url,
        token,
        data
    ):

        self.url = url
        self.data = data

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + token
        }

    def update_account(self):
        status_code = None
        try:
            res = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(self.data)
            )
        except requests.exceptions.MissingSchema as e:
            _logger.error('Encountered error in connection to SF API Update Account.')
            raise exceptions.ValidationError(e)

        response = res.json()
        _logger.info(f'SF Update Account Response: {response}')
        
        status_code = res.status_code
        state = "Success" if status_code == 200 else "Failed"

        return state

