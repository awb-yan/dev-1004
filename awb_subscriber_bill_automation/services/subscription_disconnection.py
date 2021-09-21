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

    def _get_discon_type(self, discon_type, channel):
        types = {
            "sysv": {
                "sf": {"name": "Salesforce", "value": "System, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "desc": "Subscriber Request",
                "function": "_change_status_subtype"
            },
            "sysi_expiry": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "desc": "Promo Expiry",
                "function": "_change_status_subtype"
            },
            "sysi_bandwidth": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "desc": "Bandwidth Usage Exceeded",
                "function": "_change_status_subtype"
            },
            "sysi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "System, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-temporary"},
                "ar": {"name": "Aradial", "value": ""},
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyi_nonpayment": {
                "sf": {"name": "Salesforce", "value": "Physical, Involuntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
                "desc": "Billing Non-Payment",
                "function": "_change_status_subtype"
            },
            "phyv": {
                "sf": {"name": "Salesforce", "value": "Physical, Voluntary"},
                "od": {"name": "Odoo", "value": "disconnection-permanent"},
                "ar": {"name": "Aradial", "value": ""},
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
                    "description": discon_type.get("desc"),
                    "executable": discon_type.get("function")
                }

        return False

    def _change_status_subtype(self, records, status, is_closed_subs = False, executed=False):
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

        return executed
