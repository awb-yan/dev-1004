# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import requests
import json

import logging

_logger = logging.getLogger(__name__)


class SubscriptionDisconnect(models.Model):
    _inherit = "sale.subscription"

    def prepaid_physical_discon(self):
        _logger.info('SMS:: function: prepaid_physical_discon')

        sf_update_type = 5
        max_fail_retries = 3
        main_plan = None
        date_to_discon = datetime.now()
        contacts_to_discon = self.env['res.partner'].search([('expiry_date', '>=', date_to_discon.strftime("%Y-%m-%d 00:00:00")), 
            ('expiry_date', '<=', date_to_discon.strftime("%Y-%m-%d 11:59:59"))])

        for contact in contacts_to_discon:
            latest_subs = self.env['sale.subscription'].search([('customer_number', '=', contact.customer_number)], order='id desc', limit=1)
            self._change_status_subtype(latest_subs,'disconnection-permanent', is_closed_subs = True)

            try:
                self._update_account(main_plan, latest_subs, sf_update_type, max_fail_retries)
            except:
                _logger.error(f'SMS:: !!! Failed to Update Account in SF - Update Type {sf_update_type} on Subscription code {latest_subs.code}')


    def _get_discon_type(self, discon_type, channel):
        types = {
            "sysv": {
                "sf": {"name": "Salesforce", "value": "System, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Subscriber Request",
                "function": "_change_status_subtype"
            },
            "sysi_expiry": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": True,
                "desc": "Promo Expiry",
                "function": "_change_status_subtype"
            },
            "sysi_bandwidth": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Bandwidth Usage Exceeded",
                "function": "_change_status_subtype"
            },
            "sysi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "Physical, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyv": {
                "sf": {"name": "Salesforce", "value": "Physical, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
                "subs_closed": False,
                "desc": "Subscriber Request",
                "function": "_change_status_subtype"
            },
        }

        discon_type = types.get(discon_type)
        if discon_type:
            value = discon_type.get(channel)
            if value:
                return {
                    "name": value.get("name"),
                    "status": value.get("value"),
                    "subs_closed": discon_type.get("subs_closed"),
                    "description": discon_type.get("desc"),
                    "executable": discon_type.get("function")
                }

        return False

    def _change_status_subtype(self, records, status, is_closed_subs = False, executed=False, ctp=False):
        _logger.info('function: _change_status_subtype')
        for record in records:
            if (
                record.subscription_status != "disconnection"
                or record.subscription_status_subtype != status
            ):
                if is_closed_subs:
                    record.write({
                        "subscription_status": "disconnection",
                        "subscription_status_subtype": status,
                        "stage_id" : self.env['sale.subscription.stage'].search([("name", "=", "Closed")]).id,
                        "in_progress": False
                    })
                else:
                    record.write({
                        "subscription_status": "disconnection",
                        "subscription_status_subtype": status
                    })
                executed = True
                if not ctp:
                    self._send_expirynotification(record)

        return executed

    def _send_expirynotification(self, record):
        try:            
            _logger.info(f'=== Sending Expiry Notification ===')
            _logger.debug(f'=== record {record} ===')
            self.env["awb.sms.send"]._send_subscription_notif(
                recordset=record,
                template_name="Subscription Expiry Notification",
                state="In Progress" 
            )
            _logger.debug('Completed Sending Expiry Notification')
        except:
            _logger.warning('!!! Error sending Expiry Notification')
