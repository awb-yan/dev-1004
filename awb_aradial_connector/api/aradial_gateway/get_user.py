import json
import requests
from odoo import exceptions
from requests.auth import HTTPBasicAuth

import logging

_logger = logging.getLogger(__name__)

class AradialAPIGatewayGetUser(object):
    def __init__(
        self,
        url,
        username,
        password
    ):

        self.url = url
        self.username = username
        self.password = password

    def get_user(self, sms_id_username):

        try:
            res = requests.get(
                url=self.url + "/" + sms_id_username,
                auth=HTTPBasicAuth(self.username, self.password)
            )
        except requests.exceptions.MissingSchema as e:
            raise exceptions.ValidationError(e)

        _logger.info("==== getUser Response ====")
        _logger.info(res.json())

        if res.status_code == 200:

            response = res.json()
            return response
        else:
            return False