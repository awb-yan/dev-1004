from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta

import logging


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_ids = fields.One2many('account.payment', 'bill_id', string='Payments')

    def recompute_statement(self):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice in self.invoice_line_ids:
            if invoice.product_id.product_tmpl_id.id == device_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'device_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            elif invoice.subscription_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'subs_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            else:
                data = {
                    'name': invoice.name,
                    'statement_type': 'other',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

        data = {'name': "Value Added Tax", 'statement_type': 'vat'}
        data['amount'] = self.amount_tax
        lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', self.partner_id.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('is_subscription', '=', True),
                ('invoice_origin', '!=', False),
                ('invoice_date_due', '<', self.invoice_date_due),
                ('id', '!=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="invoice_date_due desc")
        _logger.debug(f' prev_ball {invoice_id}')

        # Date Cutoffs
        start_date_cutoff = False
        end_date_cutoff = False
        if self.posting_date and self.x_studio_location:
            prev_month = self.posting_date - relativedelta(months=1)
            start_date_cutoff = prev_month.replace(day=self.x_studio_location.billing_day)
            end_date = self.posting_date.replace(day=self.x_studio_location.billing_day)
            end_date_cutoff = end_date - relativedelta(days=1)
        _logger.debug(f' Date Cutoff : {start_date_cutoff} to {end_date_cutoff} ')

        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

            total_payment = 0.0
            for payment in invoice_id.payment_ids:
                if not payment.x_studio_payment_for_receipts:
                    total_payment += payment.amount

            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': total_payment * -1,
            }
            lines.append((0, 0, prev_payment))

        # Rebates
        args_rebates = [('partner_id', '=', self.partner_id.id),
                        ('type', '=', 'out_refund'),
                        ('state', '=', 'posted'),
                        ('invoice_date', '>=', start_date_cutoff),
                        ('invoice_date', '<=', end_date_cutoff)]

        credit_note_id = self.env['account.move'].search(args_rebates, order="invoice_date desc")

        if credit_note_id:
            total_rebates = 0.0
            for rebates in credit_note_id:
                total_rebates += rebates.amount_total

            rebates = {
                'name': 'Rebates',
                'statement_type': 'adjust',
                'amount': total_rebates * -1,
            }
            lines.append((0, 0, rebates))

        # Invoice Adjustments
        adjust_args = [('partner_id', '=', self.partner_id.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_date_cutoff),
                ('invoice_date', '<=', end_date_cutoff),
        ]
        adjustments = self.env['account.move'].search(adjust_args, order="invoice_date desc")

        if adjustments:
            total_adjustments = 0.0
            for adjustment in adjustments:
                for invoice_line in adjustment.invoice_line_ids:
                    if invoice_line.product_id.name == 'Adjustment':
                        total_adjustments += invoice_line.price_unit

            if int(total_adjustments) != 0:
                adjustment = {
                    'name': 'Adjustments',
                    'statement_type': 'adjust',
                    'amount': total_adjustments
                }
                lines.append((0, 0, adjustment))

        self.update({'statement_line_ids': None})
        self.update({'statement_line_ids': lines})    

    def old_recompute_statement(self):
        self.ensure_one()
        device_id = self.env.ref('awb_subscriber_product_information.product_device_fee').id
        lines = []
        # invoice Lines
        for invoice in self.invoice_line_ids:
            if invoice.product_id.product_tmpl_id.id == device_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'device_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            elif invoice.subscription_id:
                data = {
                    'name': invoice.name,
                    'statement_type': 'subs_fee',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

            else:
                data = {
                    'name': invoice.name,
                    'statement_type': 'other',
                    'amount': invoice.price_subtotal,
                }
                lines.append((0, 0, data))

        data = {'name': "Value Added Tax", 'statement_type': 'vat'}
        data['amount'] = self.amount_tax
        lines.append((0, 0, data))

        # invoice previous bill
        args = [('partner_id', '=', self.partner_id.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('is_subscription', '=', True),
                ('invoice_date_due', '<', self.invoice_date_due),
                ('id', '!=', self.id)]

        invoice_id = self.env['account.move'].search(args, limit=1, order="invoice_date_due desc")
        _logger.debug(f' prev_ball {invoice_id}')
        if invoice_id:
            prev_bill = invoice_id.amount_total + invoice_id.total_prev_charges
            prev_bill = {
                'name': 'Previous Bill balance',
                'statement_type': 'prev_bill',
                'amount': prev_bill,
            }
            lines.append((0, 0, prev_bill))

            total_payment = 0.0
            for payment in invoice_id.payment_ids:
                total_payment += payment.amount

            prev_payment = {
                'name': 'Previous Received Payment',
                'statement_type': 'payment',
                'amount': total_payment * -1,
            }
            lines.append((0, 0, prev_payment))

        # Rebates
        args_rebates = [('partner_id', '=', self.partner_id.id),
                        ('type', '=', 'out_refund'),
                        ('state', '=', 'posted'),
                        ('invoice_date', '>=', self.start_date),
                        ('invoice_date', '<=', self.end_date)]

        credit_note_id = self.env['account.move'].search(args_rebates, order="invoice_date desc")

        if credit_note_id:
            total_rebates = 0.0
            for rebates in credit_note_id:
                total_rebates += rebates.amount_total

            rebates = {
                'name': 'Rebates',
                'statement_type': 'adjust',
                'amount': total_rebates * -1,
            }
            lines.append((0, 0, rebates))

        self.update({'statement_line_ids': None})
        self.update({'statement_line_ids': lines})
class account_payment(models.Model):
    _inherit = "account.payment"

    bill_id = fields.Many2one('account.move', string='Invoice')

    def link_to_invoice(self):
        for rec in self:
            args = [
                ('partner_id', '=', rec.partner_id.id),
                ('type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('is_subscription', '=', True),
                ('invoice_date', '<', rec.payment_date),
                # ('invoice_date_due', '>', rec.payment_date)
            ]
            invoices = self.env['account.move'].search(args, order='invoice_date_due')
            last_invoice = False
            for inv in invoices:
                last_invoice = inv
                if inv.invoice_date_due > rec.payment_date:
                    rec.bill_id = inv.id
                    break
            else:
                if last_invoice:
                    rec.bill_id = last_invoice.id
