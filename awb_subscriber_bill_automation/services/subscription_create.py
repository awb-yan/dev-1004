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

    def provision_and_activation(self, record, main_plan, last_subscription):
        _logger.info('function: provision_and_activation')

        max_retries = 3
        self.record = record

        self._set_to_draft(record)
        plan_type = main_plan.sf_plan_type.name
        aradial_flag = main_plan.sf_facility_type.is_aradial_product
        
        _logger.debug(f'Plan Type: {plan_type}')
        _logger.debug(f'Aradial Flag: {aradial_flag}')

        # Plan Type Flow routing
        if plan_type == 'Postpaid':
            add_to_timebank = self._provision_postpaid(record, last_subscription)
        else:
            add_to_timebank = self._provision_prepaid(record, last_subscription)

        _logger.debug(f'Add to Timebank: {add_to_timebank}')
        # Facility Type routing
        if aradial_flag:
            self._send_to_aradial(record, main_plan, max_retries, add_to_timebank, last_subscription)

        self._start_subscription(record, max_retries)

       
    def _set_to_draft(self, record):
        _logger.info('function: set_to_draft')
        self.record = record

        self.record['stage_id'] = self.env['sale.subscription.stage'].search([("name", "=", "Draft")]).id
        self.record['in_progress'] = False
        self.env.cr.commit()


    # TODO: update Postpaid provisioning
    def _provision_postpaid(self, record, last_subscription):
        if not last_subscription:
            _logger.debug('first')
            # Welcome Provisioning Notification
        else:
            _logger.debug('last')
            # Returning Subscriber Notification

        return 0


    def _provision_prepaid(self, record, last_subscription):
        _logger.info('function: provision_prepaid')
        
        if not last_subscription:
            _logger.debug('First subscription')
            remaining_seconds = 0
            try:
                _logger.info(' === Sending SMS Welcome Notification ===')
                # Welcome Provisioning Notification
                self.env["awb.sms.send"]._send_subscription_notif(
                    recordset=record,
                    template_name="Subscription Welcome Notification",
                    state="Draft"
                )
                _logger.debug('Completed Sending Welcome SMS')
            except:
                _logger.warning('!!! Error sending Welcome Notification')
        else:
            _logger.debug('Reloading')
            # Check if still active, query remaining days in aradial
            remaining_seconds = self.env['aradial.connector'].get_remaining_time(last_subscription.opportunity_id.jo_sms_id_username)

            # _logger.debug(' === Sending SMS CTP Notification ===')
            # # CTP Provisioning Notification
            # self.env["awb.sms.send"]._send_subscription_notif(
            #     recordset=record,
            #     template_name="Subscription Payment Notification",
            #     state="Draft"
            # )

        return remaining_seconds

    def _send_to_aradial(self, record, main_plan, max_retries, additional_time, last_subscription):
        _logger.info('function: send_to_aradial')
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
                    'Status': 0,
                    'FirstName': first_name,
                    'LastName': last_name,
                    'ServiceType': 'Internet',
                    'PrepaidIndicator': 1 if main_plan.sf_plan_type.name == 'Prepaid' else 0,
                    'TimeBank': additional_time,
                    'UseTimeBank': 1
                }

                _logger.debug(self.data)

                if not self.env['aradial.connector'].create_user(self.data):
                    raise Exception

                _logger.info('Successfully created user in Aradial')

            except:
                if max_retries > 1:
                    self._send_to_aradial(record, main_plan, max_retries-1, additional_time, last_subscription)
                else:
                    _logger.error(f'!!! Add to Failed transaction log - Subscription code {record.code}')
                    raise Exception(f'!!! Error Creating user in Aradial for {record.code}')

        else:   # CTP - Update User's TimeBank
            # 2 options to handle this:
            #     1. Update the Offer of the User in Aradial (does it add up the remaining timebank?)
            #     2. Get the remaining time and delete the user in Aradial, create new user with the additional_time
            _logger.info(f'Processing reloading for Customer: {record.code}, New Subscription: {record.code} and New Offer: {main_plan.default_code.upper()}')
    
            # for Residential
            first_name = record.partner_id.first_name
            last_name = record.partner_id.last_name

            # for Corporate
            if not first_name: 
                first_name = record.partner_id.name
                last_name = ''

            self.data = {
                'Page': 'UserEdit',
                'Modify': 1,
                'UserID': record.opportunity_id.jo_sms_id_username,
                'Password': record.opportunity_id.jo_sms_id_password,
                'TimeBank': additional_time,
                'UseTimeBank': 1,
                'Status': 0,
                'Offer': main_plan.default_code.upper(),
                'CustomInfo1': record.code,
                'CustomInfo2': record.subscriber_location_id.name,
                'CustomInfo3': record.customer_number,
                'FirstName': first_name,
                'LastName': last_name,
            }

            _logger.debug(f'Updating aradial user with data= {self.data}')

            try:
                if not self.env['aradial.connector'].update_user(self.data):
                    raise Exception
            except:
                _logger.error(f'!!! Error encountered while updating aradial user for Subscription: {record.code} and SMS UserID: {record.opportunity_id.jo_sms_id_username}')
          


    def _start_subscription(self, record, max_retries):

        _logger.info('function: start_subssubscription')

        try:
            self.record = record;
            now = datetime.now().strftime("%Y-%m-%d")
            self.record.write({
                'date_start': now,
                'stage_id': self.env['sale.subscription.stage'].search([("name", "=", "In Progress")]).id,
                'in_progress': True
            })

            # Send activation Notification ----
            try:            
                _logger.info(' === Sending SMS Activation Notification ===')
                self.env["awb.sms.send"]._send_subscription_notif(
                    recordset=self.record,
                    template_name="Subscription Activation Notification",
                    state="In Progress"
                )
                _logger.debug('Completed Sending Activation SMS')
            except:
                _logger.warning('!!! Error sending Activation Notification')

        except:
            if max_retries > 1:
                self._start_subscription(record, max_retries-1)
            else:
                _logger.error(f'!!! Error encountered while starting subscription for {self.record.code}..')
                raise Exception(f'!!! Error encountered while starting subscription for {self.record.code}..')


    def generate_atmref(self, record, max_retries):

        _logger.info('function: generate_atmref')
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
                self._generate_atmref(record, max_retries-1)
            else:
                _logger.error(f'!!! Error encountered while generating atm reference for subscription {self.record.code}..')
                raise Exception(f'!!! Error encountered while generating atm reference for subscription {self.record.code}..')

