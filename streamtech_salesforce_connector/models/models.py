# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, exceptions, _
from simple_salesforce import Salesforce
from openerp import _
from openerp.exceptions import Warning, ValidationError
from odoo.osv import osv
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class StreamtechSalesForceSettingModel(models.TransientModel):
    _inherit = 'res.config.settings'

    sf_sandbox = fields.Boolean(string="SF Sandbox", default=False)

    def get_log(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Salesforce Logs',
            'view_mode': 'tree',
            'res_model': 'sync.history',
            'context': "{'create': False}"
        }

    @api.model
    def set_values(self):
        res = super(StreamtechSalesForceSettingModel, self).set_values()
        self.env['ir.config_parameter'].set_param('odoo_salesforce.sf_sandbox', self.sf_sandbox)

        return res

    @api.model
    def get_values(self):
        res = super(StreamtechSalesForceSettingModel, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        sandbox = IrConfigParameter.get_param('odoo_salesforce.sf_sandbox')

        res.update(
            sf_sandbox=True if sandbox == 'True' else False
        )

        return res

    def test_credentials(self):
        """
        Tests the user SalesForce account credentials

        :return:
        """
        _logger.info('streamtech_salesforce_connector: test_credentials')

        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            username = IrConfigParameter.get_param('odoo_salesforce.sf_username')
            password = IrConfigParameter.get_param('odoo_salesforce.sf_password')
            security = IrConfigParameter.get_param('odoo_salesforce.sf_security_token')
            sandbox = IrConfigParameter.get_param('odoo_salesforce.sf_sandbox')
            if sandbox:
                sf = Salesforce(username=username, password=password, security_token=security, domain="test")
            else:
                sf = Salesforce(username=username, password=password, security_token=security)
            # query = "select id,name,title,email,phone,city,country,postalCode, state, street from User"
            # extend_query = " where email='" + self.env.user.email + "'"
            # user = sf.query(query + extend_query)["records"][0]
            # user = sf.query(query + extend_query)["records"][0]
            # odoo_user = self.env['res.users'].search([('email', '=', user['Email'])])
            # if odoo_user:
            #     odoo_user.write({
            #         'salesforce_id': user['Id'],
            #     })
            #     self.env.cr.commit()

            # if not odoo_user:
            #     if user['Title']:
            #         user_title = self.env['res.partner.title'].search([('name', '=', user['Title'])])
            #         if not user_title:
            #             user_title = self.env['res.partner.title'].create({
            #                 'name': user['Title']
            #             })
            #     user = self.env['res.users'].create({
            #         'salesforce_id': user['Id'],
            #         'name': user['Name'] if user['Name'] else None,
            #         'login': user['Email'] if user['Email'] else None,
            #         'phone': user['Phone'] if user['Phone'] else None,
            #         'email': user['Email'] if user['Email'] else None,
            #         'city': user['City'] if user['City'] else None,
            #         'street': user['Street'] if user['Street'] else None,
            #         'zip': user['PostalCode'] if user['PostalCode'] else None,
            #         'state_id': self.env['res.country.state'].search(
            #             [('name', '=', user['State'])]).id if
            #         user['State'] else None,
            #         'title': user_title.id if user_title else None,
            #     })


        except Exception as e:
            raise Warning(_(str(e)))

        raise osv.except_osv(_("Success!"), (_("Credentials are successfully tested.")))
