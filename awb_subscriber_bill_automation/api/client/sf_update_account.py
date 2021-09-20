from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class SalesForceConnector(models.Model):
    _inherit = "sale.subscription"

    def update_account(self, record=None, update_type=None, main_plan=None):
        _logger.info('function: SalesForceConnector => update_account')
        
        if record:
            self.data = {}
            if update_type == 6:
                _logger.info('Entered update_type equal to 6')
                self.data = {
                    'SFID': record.opportunity_id.salesforce_id,
                    'SMS_Activation_Date_Time': record.date_start.strftime("%m/%d/%Y %I:%M%p"),
                    'SubscriptionCode': record.code,
                    'AccountStatus': "Active",
                    'ProductCode': main_plan.default_code.upper(),
                    'UpdateType': update_type
                }
            elif update_type == 7:
                _logger.info('Entered update_type equal to 6')
                self.data = {
                    'SFID': record.opportunity_id.salesforce_id,
                    'SubscriptionCode': record.code,
                    'AccountStatus': "Active",
                    'ProductCode': main_plan.default_code.upper(),
                    'UpdateType': update_type
                }

            _logger.info(f'SF Data to Update: {self.data}')
            update_account_stat = self.env['salesforce.connector'].update_account(self.data)   
        else:
            _logger.error('!!! No SF Account to Update')
            update_account_stat = 'Failed'
            raise Exception('!!! No SF Account to Update')
  
        _logger.info(f'SF Update Account Status: {update_account_stat}')
        return update_account_stat



