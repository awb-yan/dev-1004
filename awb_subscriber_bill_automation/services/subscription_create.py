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

import logging

_logger = logging.getLogger(__name__)


class SubscriptionCreate(models.Model):
    _inherit = "sale.subscription"

    def provision_and_activation(self, record, main_plan, last_subscription, ctp):
        _logger.info('SMS:: function: provision_and_activation')

        max_retries = 3
        self.record = record

        self._set_to_draft(record)
        plan_type = main_plan.sf_plan_type.name
        aradial_flag = main_plan.sf_facility_type.is_aradial_product
        
        _logger.debug(f'SMS:: Plan Type: {plan_type}')
        _logger.debug(f'SMS:: Aradial Flag: {aradial_flag}')

        # Plan Type Flow routing
        if plan_type == 'Postpaid':
            self._provision_postpaid(record, last_subscription)
        else:
            self._provision_prepaid(record, last_subscription)

        # Facility Type routing
        if aradial_flag:
            self._send_to_aradial(record, main_plan, max_retries, last_subscription)

        self._start_subscription(record, max_retries, ctp)

       
    def _set_to_draft(self, record):
        _logger.info('SMS:: function: set_to_draft')
        self.record = record

        self.record['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        self.record['in_progress'] = False
        self.env.cr.commit()


    # TODO: update Postpaid provisioning
    def _provision_postpaid(self, record, last_subscription):
        if not last_subscription:
            _logger.debug('SMS:: first')
            # Welcome Provisioning Notification
        else:
            _logger.debug('SMS:: last')
            # Returning Subscriber Notification

        return 0

    def _provision_prepaid(self, record, last_subscription):
        _logger.info('SMS:: function: provision_prepaid')
        
        if not last_subscription:
            _logger.debug('SMS:: First subscription')
            try:
                _logger.info(' === Sending SMS Welcome Notification ===')
                # Welcome Provisioning Notification
                self.env["awb.sms.send"]._send_subscription_notif(
                    recordset=record,
                    template_name="Subscription Welcome Notification",
                    state="Draft"
                )
                _logger.debug('SMS:: Completed Sending Welcome SMS')
            except:
                _logger.warning('SMS:: !!! Error sending Welcome Notification')
        else:
            _logger.debug('SMS:: Reloading...')


    def _send_to_aradial(self, record, main_plan, max_retries, last_subscription):
        _logger.info('SMS:: function: send_to_aradial')
        # New Subscription
        if not last_subscription:
            try:
                # for Residential
                first_name = record.partner_id.first_name
                last_name = record.partner_id.last_name

                # for Corporate
                if not first_name: 
                    first_name = record.partner_id.name
                    last_name = ''

                self.data = {
                    'UserID': record.opportunity_id.jo_sms_id_username,
                    'Password': record.opportunity_id.jo_sms_id_password,
                    'CustomInfo1': record.code,
                    'CustomInfo2': record.subscriber_location_id.name,
                    'CustomInfo3': record.customer_number,
                    'Offer': main_plan.default_code.upper(),
                    # 'StartDate': record.date_start.strftime("%m/%d/%Y, %H:%M:%S"),
                    'Status': '0',
                    'FirstName': first_name,
                    'LastName': last_name,
                    'ServiceType': 'Internet',
                    'PrepaidIndicator': 1 if main_plan.sf_plan_type.name == 'Prepaid' else 0,
                }

                _logger.debug(f'SMS:: Creating User with data: {self.data}')

                if not self.env['aradial.connector'].create_user(self.data):
                    raise Exception

                _logger.info('SMS:: Successfully created user in Aradial')

            except:
                if max_retries > 1:
                    self._send_to_aradial(record, main_plan, max_retries-1, last_subscription)
                else:
                    _logger.error(f'SMS:: !!! Add to Failed transaction log - Subscription code {record.code}')
                    raise Exception(f'SMS:: !!! Error Creating user in Aradial for {record.code}')

        else:   # CTP - Update User's TimeBank
            # 2 options to handle this:
            #     1. Update the Offer of the User in Aradial (does it add up the remaining timebank?)
            #     2. Get the remaining time and delete the user in Aradial, create new user with the additional_time
            _logger.info(f'SMS:: Processing reloading for Customer: {record.code}, New Subscription: {record.code} and New Offer: {main_plan.default_code.upper()}')
    
            # for Residential
            first_name = record.partner_id.first_name
            last_name = record.partner_id.last_name

            # for Corporate
            if not first_name: 
                first_name = record.partner_id.name
                last_name = ''

            self.data = {
                'UserID': record.opportunity_id.jo_sms_id_username,
                'Password': record.opportunity_id.jo_sms_id_password,
                'Status': '0',
                'Offer': main_plan.default_code.upper(),
                'Timebank': self._getTimebank(main_plan.default_code.upper()),
                'CustomInfo1': record.code,
                'CustomInfo2': record.subscriber_location_id.name,
                'CustomInfo3': record.customer_number,
                'FirstName': first_name,
                'LastName': last_name,
            }

            _logger.info(f'SMS:: Updating aradial user with data= {self.data}')

            try:
                if not self.env['aradial.connector'].update_user(self.data):
                    raise Exception
            except:
                if max_retries > 1:
                    self._send_to_aradial(record, main_plan, max_retries-1, last_subscription)
                else:
                    _logger.error(f'SMS:: !!! Error encountered while updating aradial user for Subscription: {record.code} and SMS UserID: {record.opportunity_id.jo_sms_id_username}')
                    raise Exception(f'SMS:: !!! Error encountered while updating aradial user for Subscription: {record.code} and SMS UserID: {record.opportunity_id.jo_sms_id_username}')


    def _start_subscription(self, record, max_retries, ctp):

        _logger.info('SMS:: function: start_subscription')

        try:
            self.record = record
            now = datetime.now().strftime("%Y-%m-%d")
            self.record.write({
                'date_start': now,
                'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
                'in_progress': True
            })

            # Send Activation or CTP Notification ----
            smstemplate = "Subscription Activation Notification"
            if ctp:
                smstemplate = "Subscription CTP Notification"
            
            try:            
                _logger.info(f'SMS::  === Sending {smstemplate} ===')
                self.env["awb.sms.send"]._send_subscription_notif(
                    recordset=self.record,
                    template_name=smstemplate,
                    state="In Progress"
                )
                _logger.debug(f'SMS:: Completed Sending {smstemplate}')
            except:
                _logger.warning(f'SMS:: !!! Error sending {smstemplate}')

        except:
            if max_retries > 1:
                self._start_subscription(record, max_retries-1)
            else:
                _logger.error(f'SMS:: !!! Error encountered while starting subscription for {self.record.code}..')
                raise Exception(f'SMS:: !!! Error encountered while starting subscription for {self.record.code}..')

    def generate_atmref(self, record, max_retries):

        _logger.info('SMS:: function: generate_atmref')
        try:
            self.record = record
            company = self.record.company_id

            code_seq = company.company_code.filtered(
                lambda code: code.is_active == True
            )

            if not code_seq:
                raise UserError("No Active company code, Please check your company code settings")

            self.record.write({
                'atm_ref_sequence': code_seq[0]._get_seq_count()
            })

        except:
            if max_retries > 1:
                self.generate_atmref(record, max_retries-1)
            else:
                _logger.error(f'SMS:: !!! Error encountered while generating atm reference for subscription {self.record.code}..')
                raise Exception(f'SMS:: !!! Error encountered while generating atm reference for subscription {self.record.code}..')

    def _getTimebank(self, offer):

        if offer == 'PREPAIDFBR5DAYS':
            return 5 * 86400
        elif offer == 'PREPAIDFBR10DAYS':
            return 10 * 86400
        elif offer == 'PREPAIDFBR15DAYS':
            return 15 * 86400
        elif offer == 'PREPAIDFBR30DAYS':
            return 30 * 86400
        
        return 0