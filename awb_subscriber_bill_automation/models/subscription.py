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
from  pytz import timezone

import json

import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    account_identification = fields.Char(string="Account ID")
    customer_number = fields.Char(related='partner_id.customer_number')
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    subscription_status = fields.Selection([('new', 'New'),
                                            ('upgrade', 'Upgrade'),
                                            ('convert', 'Convert'),
                                            ('downgrade', 'Downgrade'),
                                            ('transfer', 'Transfer'),
                                            ('re-contract', 'Re-contract'),
                                            ('pre-termination', 'Pre-Termination'),
                                            ('disconnection', 'Disconnection'),
                                            ('reconnection', 'Reconnection')], default='new', string="Subscription Status")
    subscription_status_subtype = fields.Selection([('disconnection-permanent', 'Permanent Discon'),
                                            ('disconnection-temporary', 'Temporary Discon')], string="Subscription Status Subtype")

    atm_ref = fields.Char(string="ATM Reference", store=True, compute='_compute_atm_reference_number')
    atm_ref_sequence = fields.Char(string="ATM Reference Sequence", store=True)

    state = fields.Char("State", compute='_get_stage_name')
    product_names = fields.Char("Products", compute='_get_subs_product_names')
    product_desc = fields.Char("Products Description", compute='_get_subs_product_names')
    datetime_now = fields.Char("Date and Time", compute='_get_datetime_now')

    # New Fields

    plan_type = fields.Many2one('product.plan.type', compute='_compute_plan_type', store=True)

    # Business Logic

    @api.depends('recurring_invoice_line_ids')
    def _compute_plan_type(self):
        for rec in self:
            plan_type_id = []
            for lines in rec.recurring_invoice_line_ids:
                if lines.product_id.product_tmpl_id.product_segmentation == 'month_service':
                    plan_type_id = lines.product_id.product_tmpl_id.sf_plan_type
                    # plan_type_result = self.env['product.plan.type'].search([('id','=',plan_type_id)])

            rec.plan_type = plan_type_id


    @api.model
    def create(self, vals):
        # Commenting this for now
        # Origin code
        # vals['atm_ref_sequence'] = self.env['ir.sequence'].next_by_code('subscription.atm.reference.seq.code')
        res = super(SaleSubscription, self).create(vals)

        _logger.info('SMS::function: create')
        self.record = res
        sms_flag = True
        plan_type = ''
        max_fail_retries = 3
        ctp = False
        last_subs_main_plan = False

        try:
            main_plan = self._get_mainplan(self.record)        
            _logger.debug(f'SMS::Main_Plan: {main_plan}')

            plan_type = main_plan.sf_plan_type.name
            if plan_type == 'Postpaid':
                sms_flag = False

        except:
            _logger.warning("SMS:: Main Plan not found")
            sms_flag = False

        if sms_flag and plan_type == 'Prepaid':
            sf_update_type = 6
            last_subscription = self._get_last_subscription(self.record, plan_type)

            # CTP flow for prepaid, 
            if last_subscription:
                ctp = True   
                last_subs_main_plan = self._get_mainplan(last_subscription)        
                
                self.record = self._update_new_subscription(self.record, last_subscription)
                # self.record.opportunity_id = last_subscription.opportunity_id
                # Process System Discon
                sf_update_type = 7
                try:
                    is_closed_subs = True
                    subtype = "disconnection-temporary"
                    self.env['sale.subscription']._change_status_subtype(last_subscription, subtype, is_closed_subs, ctp=ctp)
                except:
                    _logger.error(f'SMS:: !!! Failed Temporary Discon - Subscription code {self.record.code}')

            self.env['sale.subscription'].provision_and_activation(self.record, main_plan, last_subscription, last_subs_main_plan, ctp)

            # Helper to update Odoo Opportunity
            try:
                self._update_account(main_plan, self.record, sf_update_type, max_fail_retries)
            except:
                _logger.error(f'SMS:: !!! Failed SF Account Update - Subscription code {self.record.code}')            

        if not ctp:
            self.env['sale.subscription'].generate_atmref(self.record, max_fail_retries)

        return res

    # TODO For Clean up, refer to compute plan type
    def _get_mainplan(self, record):
        _logger.info('SMS:: function: get_mainplan')

        main_plan = ''

        for line_id in record.recurring_invoice_line_ids:
            if line_id.product_id.product_tmpl_id.product_segmentation == 'month_service':
                main_plan = line_id.product_id.product_tmpl_id
        
        if main_plan == '':
            raise Exception

        return main_plan  


    def _get_last_subscription(self, record, plan_type):
        _logger.info('SMS:: function: _get_last_subscription')
        customer_id = record.customer_number

        _logger.debug(f'SMS:: Subscription Code: {record.code}')
        
        _logger.debug(f'SMS:: Customer Number: {customer_id}')

        last_subscription = False
        subscriptions = self.env['sale.subscription'].search([('customer_number','=', customer_id),('plan_type','=', plan_type)], order='id desc', limit=2)
        
        if len(subscriptions) == 2:
            last_subscription = subscriptions[1]
            _logger.debug(f'SMS::_get_last_subscription subscription[0]: {subscriptions[0].code}, subscription[1]: {subscriptions[1].code}')

        return last_subscription


    def _update_account(self, main_plan, rec, sf_update_type, max_retries):
        _logger.debug(f'SMS:: _update_account')
        try:
            self.env['sale.subscription'].update_account(rec, sf_update_type, main_plan)
        except:
            if max_retries > 1:
                self._update_account(main_plan, rec, sf_update_type, max_retries-1)
            else:
                _logger.error(f'SMS:: !!! Failed SF Update Account Status - Subscription code {rec.code}')
                raise Exception(f'!!! Failed SF Update Account Status - Subscription code {rec.code}')
    
    def _update_new_subscription(self, record, last_subscription):
        _logger.info('SMS:: function: _update_new_subscription')

        self.record = record
        self.record['opportunity_id'] = last_subscription.opportunity_id.id
        self.record['atm_ref'] = last_subscription.atm_ref
        
        self.env.cr.commit()

        _logger.debug(f'SMS:: New Subscription: {self.record}')
        return self.record


    # @api.model
    # def update(self, vals):
    #     if(subscription_status == 'Disconnected')
        
    #     elif(subscription_status == 'Convert')
        
    #     elif(subscription_status == 'Upgrade')

    #     elif(subscription_status == 'Downgrade')

    @api.depends("atm_ref_sequence")
    def _compute_atm_reference_number(self):
        _logger.debug(f'SMS:: _compute_atm_reference_number')
        for rec in self:
            rec.atm_ref = ''
            if rec.atm_ref_sequence:
                company_code = self.company_id.company_code.filtered(
                    lambda code: code.is_active == True
                )
                if company_code.exists():
                    company_code = company_code[0]
                    sequence = rec.atm_ref_sequence
                    to_compute = company_code.name + sequence
                    _logger.debug(f"to_compute {to_compute}")

                    computables = str(to_compute)[2:9]
                    num_list = [8,7,6,5,4,3,2]

                    total = 0
                    for i, digit in enumerate(str(computables)):
                        product = int(digit) * num_list[i]
                        total += product

                    remainder = total % 11
                    if(
                        (
                            len(str(remainder)) > 1
                            and str(remainder)[1] == '0'
                        )
                        or str(remainder) == '0'
                    ):
                        remainder = str(remainder)[0]
                    else:
                        remainder = 11 - int(remainder)

                    _logger.debug(f"remainder {remainder}")
                    remainder = str(remainder)[0]
                    value = f'{to_compute}{remainder}1231'
                    rec.atm_ref = value

                    company_code._update_active_code()

    def _prepare_renewal_values(self, product_lines, opportunity_id):
        res = dict()
        for subscription in self:
            fpos_id = self.env['account.fiscal.position'].with_context(
                force_company=subscription.company_id.id).get_fiscal_position(subscription.partner_id.id)
            addr = subscription.partner_id.address_get(['delivery', 'invoice'])
            sale_order = subscription.env['sale.order'].search(
                [('order_line.subscription_id', '=', subscription.id)],
                order="id desc", limit=1)
            res[subscription.id] = {
                'pricelist_id': subscription.pricelist_id.id,
                'partner_id': subscription.partner_id.id,
                'partner_invoice_id': addr['invoice'],
                'partner_shipping_id': addr['delivery'],
                'currency_id': subscription.pricelist_id.currency_id.id,
                'order_line': product_lines,
                'analytic_account_id': subscription.analytic_account_id.id,
                'subscription_management': 'renew',
                'origin': subscription.code,
                'note': subscription.description,
                'fiscal_position_id': fpos_id,
                'user_id': subscription.user_id.id,
                'payment_term_id': sale_order.payment_term_id.id if sale_order else subscription.partner_id.property_payment_term_id.id,
                'company_id': subscription.company_id.id,
                'opportunity_id': opportunity_id,
            }
        return res

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        res = super(SaleSubscription, self)._prepare_invoice_line(
            line, fiscal_position, date_start, date_stop)

        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        ext_id = self.env.ref('awb_subscriber_product_information.product_ext_fee').id
        # For New Subscriber
        # if line.product_id and :
        subs_date_start = self.date_start

        if line.product_id.id not in (device_id, ext_id):
            _logger.debug(f'Check Proration {date_start} {date_stop} x {line.date_start} {line.date_end}')
            date_end = date_stop
            diff = None
            # if line ends earlier
            if line.date_end and line.date_end < date_stop:
                date_end = line.date_end
                diff = date_stop - date_end

            # if line started later than the cutoff
            if line.date_start and date_start < line.date_start:
                diff = date_end - line.date_start
            elif not line.date_start and subs_date_start > date_start:
                diff = date_end - subs_date_start

            month_factor = 31
            if diff:
                days = diff.days
            else:
                days = month_factor

            count = 0
            if days < month_factor:
                count = days / month_factor
                # original_amount = res['price_unit']
                # rate = original_amount * 12 / 365
                # new_amount = rate * days
                res['quantity'] = round(count,2)
                res['name'] += f' ({days} days)'
            _logger.debug(f'Prorate: {diff} = {count} {line} {fiscal_position} {date_start} {date_stop}')
        # if self.subscription_status == 'new' and diff.days < 31:
        return res

    def _prepare_invoice_lines(self, fiscal_position):
        self.ensure_one()
        if not self.subscriber_location_id.cutoff_day:
            raise UserError('No Zone is assigned to subscriber location. Please assign a zone on subscriber record.')
        cutoff_day = self.subscriber_location_id.cutoff_day
        next_date = self.recurring_next_date

        if not next_date:
            raise UserError(_('Please define Date of Next Invoice of "%s".') % (self.display_name,))

        periods = {'daily': 'days', 'weekly': 'weeks',
                   'monthly': 'months', 'yearly': 'years'}
        interval_type = periods[self.recurring_rule_type]
        interval = self.recurring_interval

        if cutoff_day < 16:
            next_date = next_date - relativedelta(**{interval_type: interval})
        else:
            next_date = next_date - relativedelta(**{interval_type: interval*2})

        _logger.debug(f'Compute next date: Next {next_date}, due_day: {cutoff_day}')
        recurring_start_date = self._get_recurring_next_date(self.recurring_rule_type, interval, next_date, cutoff_day)
        revenue_date_start = fields.Date.from_string(recurring_start_date+relativedelta(days=1))
        _logger.debug('Dates: Next Date: {next_date} Start Day: {revenue_date_start}')
        recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, 0, revenue_date_start, cutoff_day)
        _logger.debug(f'Days: {recurring_start_date >= recurring_next_date}: {recurring_start_date} > {recurring_next_date}')
        # This is a HACK to fix the issue with jumping dates
        if recurring_start_date >= recurring_next_date:
            recurring_next_date = self._get_recurring_next_date(self.recurring_rule_type, interval, revenue_date_start, cutoff_day)

        revenue_date_stop = fields.Date.from_string(recurring_next_date)
        invoice_lines = []
        for line in self.recurring_invoice_line_ids:
            starts_within = not line.date_start or (line.date_start and line.date_start < revenue_date_stop)
            ends_within = not line.date_end or (line.date_end and line.date_end > revenue_date_start)
            _logger.debug(f'Check Invoice line dates: {starts_within} {line.date_start} {revenue_date_stop}')
            _logger.debug(f'Check Invoice line dates: {ends_within} {line.date_end} {revenue_date_start}')
            if starts_within and ends_within:
                val = self._prepare_invoice_line(
                    line, fiscal_position, revenue_date_start, revenue_date_stop)
                invoice_lines.append((0, 0, val))
        return invoice_lines

    def _prepare_invoice_statement(self, invoice):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice_line in invoice['invoice_line_ids']:
            line = invoice_line[2]
            _logger.debug(f'Line: {line}')
            product = self.env['product.product'].browse(line['product_id'])
            _logger.debug(f'Prod ID temp {product.product_tmpl_id.id}')

            total_vat = 0.0
            for taxes in line['tax_ids']:
                vat = taxes[2]
                args = [('id', 'in', vat)]
                tax = self.env['account.tax'].search(args)
                total_price_unit = line['price_unit'] * \
                    line['quantity']  # 1999
                tot_vat = 0.0
                for t in tax:
                    total_price_unit = total_price_unit - tot_vat
                    # tax exclusive
                    # total_vat += total_price_unit * tax.amount / 100
                    # tax inclusive
                    tot_vat += (total_price_unit /
                                ((100 + t.amount) / 100)) * (t.amount/100)
                total_vat += tot_vat

            if product.product_tmpl_id.id != device_id:
                _logger.debug(f'Invoice: {invoice}')

                args = [('partner_id', '=', invoice['partner_id']),
                        ('type', '=', 'out_refund'),
                        ('state', '=', 'posted'),
                        ('invoice_date', '>=', line['subscription_start_date']),
                        ('invoice_date', '<=', line['subscription_end_date'])]

                credit_note_id = self.env['account.move'].search(args, limit=1, order="invoice_date desc")

                rebates = {
                    'name': 'Rebates',
                    'statement_type': 'adjust',
                    'amount': credit_note_id.amount_total * -1,
                }
                lines.append((0, 0, rebates))

            if product.product_tmpl_id.id == device_id:
                data = {
                    'name': line['name'],
                    'statement_type': 'device_fee',
                    'amount': line['price_unit'] - total_vat,
                }
                lines.append((0, 0, data))
            else:
                data = {
                    'name': line['name'],
                    'statement_type': 'subs_fee',
                    'amount': (line['price_unit'] * line['quantity']) - total_vat,
                }
                lines.append((0, 0, data))

            data = {'name': "Value Added Tax", 'statement_type': 'vat'}
            data['amount'] = total_vat
            lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', invoice['partner_id']),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_line_ids.subscription_id', '=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="end_date desc")

        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

        #Previous Payment
        args_pay = [('partner_id', '=', invoice['partner_id']),
                    ('partner_type', '=', 'customer'),
                    ('invoice_ids', 'in', invoice_id.id),
                    ('state', '=', 'posted')]
        payment_id = self.env['account.payment'].search(args_pay, limit=1, order="payment_date desc")


        if payment_id:
            prev_payment = payment_id.amount
            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': prev_payment * -1,
            }
            lines.append((0, 0, prev_payment))

        return lines

    def _prepare_invoice(self):
        invoice = super(SaleSubscription, self)._prepare_invoice()
        invoice['atm_subscription_ref'] = self.atm_ref
        invoice['statement_line_ids'] = self._prepare_invoice_statement(invoice)
        return invoice

    def prepare_renewal(self, product_lines, opportunity_id):
        self.ensure_one()
        values = self._prepare_renewal_values(product_lines, opportunity_id)
        order = self.env['sale.order'].create(values[self.id])
        order.message_post(body=(_("This renewal order has been created from the subscription ") +
                                 " <a href=# data-oe-model=sale.subscription data-oe-id=%d>%s</a>" % (self.id, self.display_name)))
        order.order_line._compute_tax_id()
        _logger.debug(f'Order pro {order}')
        _logger.debug(f'Order product_lines {product_lines}')
        order.action_confirm_renewal()

    def wipe(self):
        self.write({"recurring_invoice_line_ids": [(6, 0, [])]})

    @api.onchange('date_start', 'template_id')
    def onchange_date_start(self):
        if self.date_start and self.recurring_rule_boundary == 'limited' and self.opportunity_id:
            periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
            contract_term = self.opportunity_id.contract_term
            self.date = fields.Date.from_string(self.date_start) + relativedelta(**{
                periods[self.recurring_rule_type]: contract_term * self.template_id.recurring_interval})
        else:
            self.date = False

    @api.depends('stage_id')
    def _get_stage_name(self):
        for rec in self:
            rec.state = rec.stage_id.name


    @api.depends('recurring_invoice_line_ids')
    def _get_subs_product_names(self):
        _logger.info('function: get_subs_product_names')
        products = []
        desc = []
        for rec in self:
            for line_item in rec.recurring_invoice_line_ids:
                if line_item.product_id.product_segmentation == 'month_service':
                    _logger.debug("MSF")
                    _logger.debug(f'Name: {line_item.product_id.name}')
                    _logger.debug(f'Description: {line_item.product_id.description}')
                    products.append(line_item.product_id.name)
                    desc.append(line_item.product_id.description)
                
            if not desc:
                desc = ''          
           
            rec.product_names = ', '.join(products)
            rec.product_desc = ', '.join(desc)


    def _get_datetime_now(self):
        _logger.info(f'SMS:: function: _get_datetime_now')    
        try:
            # Current time in UTC
            now_utc = datetime.now(timezone('UTC'))
            # Convert to Asia/Manila time zone
            now = now_utc.astimezone(timezone('Asia/Manila'))
            for rec in self:
                rec.datetime_now = now.strftime("%m/%d/%Y %I:%M %p")
                _logger.debug(f'SMS::rec.datetime_now {rec.datetime_now}')
        except:
            _logger.error(f'SMS:: Error encountered in getting date and time..') 
            rec.datetime_now = datetime.now().strftime("%m/%d/%Y %I:%M %p")
    


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_end = fields.Date(string='End Date')
