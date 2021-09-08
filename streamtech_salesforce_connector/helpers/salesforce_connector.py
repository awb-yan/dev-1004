from odoo import models, fields, api, exceptions, _
from simple_salesforce import Salesforce
from openerp.exceptions import Warning

class SalesForceConnect(object):
    def connect_salesforce(self, model):
        IrConfigParameter = model.env['ir.config_parameter'].sudo()
        username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
        password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
        security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
        sandbox = IrConfigParameter.get_param('odoo_salesforce.sf_sandbox')

        if sandbox:
            sales_force = Salesforce(username=username, password=password, security_token=security, domain="test")
        else:
            sales_force = Salesforce(username=username, password=password, security_token=security)

        return sales_force


