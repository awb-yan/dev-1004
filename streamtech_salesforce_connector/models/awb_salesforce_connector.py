from ..api.sf_gateway.authentication import SalesforceAPIGatewayAuth
from ..api.sf_gateway.update_account import SalesforceAPIGatewayUpdateAccount
from odoo import api, fields, models, exceptions, _
import logging

_logger = logging.getLogger(__name__)

class AWBSFConnector(models.Model):
    _inherit = 'salesforce.connector'

    def _check_sf_api_params(
        self,
        sf_api_auth_url,
        sf_api_url,
        sf_api_client_id,
        sf_api_client_secret,
        sf_username,
        sf_password,
        sf_token
    ):
        _logger.info('------------------- SF Check System Parameters start')
        error = []
        if not sf_api_auth_url or not sf_api_url or not sf_api_client_id or not sf_api_client_secret:
            error.append("SF API Required Credentials")
        if not sf_username or not sf_password or not sf_token:
            error.append("SF Required Credentials")
        if error:
            _logger.error('SF API System Parameters are not set.')
            raise exceptions.ValidationError(
                ("%s are not set, You can configure this on Settings > Technical > Parameters > System Parameters") % (
                    ", ".join(error)
                )
            )
        
        _logger.info('------------------- SF Check System Parameters end')
        

    def authenticate(
        self, 
        url, 
        client_id, 
        client_secret, 
        username, 
        password
    ):

        _logger.info('------------------- SF Authentication start')

        sf_api = SalesforceAPIGatewayAuth(
            url=url
        )
        token = sf_api.authenticate(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password
        )

        _logger.info('------------------- SF Authentication end')
        return token

    def update_account(self, data):

        _logger.info('------------------- SF Update Account start')

        sf_sys_params = self.env['ir.config_parameter'].sudo()
        sf_username = sf_sys_params.get_param('odoo_salesforce.sf_username')
        sf_password = sf_sys_params.get_param('odoo_salesforce.sf_password')
        sf_token = sf_sys_params.get_param('odoo_salesforce.sf_security_token')
        sf_api_url = sf_sys_params.get_param('odoo_salesforce.sf_api_url')
        sf_api_auth_url = sf_sys_params.get_param('odoo_salesforce.sf_api_auth_url')
        sf_api_client_id = sf_sys_params.get_param('odoo_salesforce.sf_api_client_id')
        sf_api_client_secret = sf_sys_params.get_param('odoo_salesforce.sf_api_client_secret')
        
        self._check_sf_api_params(
            sf_api_auth_url,
            sf_api_url,
            sf_api_client_id,
            sf_api_client_secret,
            sf_username,
            sf_password,
            sf_token
        )

        token = self.authenticate(
            sf_api_auth_url,
            sf_api_client_id,
            sf_api_client_secret,
            sf_username,
            sf_password + sf_token
        )

        account = SalesforceAPIGatewayUpdateAccount(
            url=sf_api_url,
            token=token,
            data=data
        )
        updated_acct = account.update_account()

        _logger.info(f'SF Account Update: {updated_acct}')
        _logger.info('------------------- SF Update Account end')
        return updated_acct
        

