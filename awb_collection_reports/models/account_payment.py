# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    current = fields.Float(string='Current', default=0, compute='_compute_current', store=True)
    arrears = fields.Float(string='Arrears', default=0, compute='_compute_arrears',store=True)
    advances = fields.Float(string='Advances', default=0, compute='_compute_advances', store=True)

    @api.depends('reconciled_invoice_ids','invoice_line','amount')
    def _compute_current(self):
        for record in self:
            
            due_date = False
            amount = 0
            if record.invoice_line:
                for invoice in record.invoice_line:
                    due_date = invoice.due_date
                    if due_date:
                        if due_date >= record.payment_date:
                            amount += invoice.paid_amount
                        else:
                            amount = 0
                    else:
                        amount = 0
                record.current = amount

            if not record.invoice_line:
                for invoice in record.reconciled_invoice_ids:
                    due_date = invoice.invoice_date_due
                    # line_total = 0
                    if due_date:
                        if due_date >= record.payment_date:
                            # for payment in invoice.payment_ids.filtered(lambda x: x.id == record.id):
                            # for lines in invoice.invoice_line_ids:
                                # line_total += lines.price_subtotal
                            if invoice.amount_total <= record.amount:
                                # amount = line_total
                                amount = invoice.amount_total
                            elif invoice.amount_total > record.amount:
                                amount = record.amount
                            else:
                                amount = 0
                    else:
                        pay_term = invoice.invoice_payment_term_id.line_ids
                        term_day = 0
                        for pay in pay_term:
                            term_day = pay.days
                            break 
                        due_date = invoice.invoice_date + relativedelta(days=term_day)
                        if due_date:
                            if due_date >= record.payment_date:
                                # for payment in invoice.payment_ids.filtered(lambda x: x.id == record.id):
                                # for lines in invoice.invoice_line_ids:
                                    # line_total += lines.price_subtotal
                                if invoice.amount_total <= record.amount:
                                    # amount = line_total
                                    amount = invoice.amount_total
                                elif invoice.amount_total > record.amount:
                                    amount = record.amount
                                else:
                                    amount = 0
                record.current = amount

    @api.depends('reconciled_invoice_ids','invoice_line','amount')
    def _compute_arrears(self):
        for record in self:

            due_date = False
            amount = 0
            if record.invoice_line:
                for invoice in record.invoice_line:
                    due_date = invoice.due_date
                    if due_date:
                        if due_date < record.payment_date:
                            amount += invoice.paid_amount
                        else:
                            amount = 0
                record.arrears = amount
                        
            if not record.invoice_line:
                for invoice in record.reconciled_invoice_ids:
                    due_date = invoice.invoice_date_due
                    line_total = 0
                    if due_date:
                        if due_date < record.payment_date:
                            # for payment in invoice.payment_ids.filtered(lambda x: x.id == record.id):
                            # for lines in invoice.invoice_line_ids:
                            #     line_total += lines.price_subtotal
                            if invoice.amount_total <= record.amount:
                                # amount = line_total
                                amount = invoice.amount_total
                            elif invoice.amount_total > record.amount:
                                amount = record.amount
                            else:
                                amount = 0
                    else:
                        pay_term = invoice.invoice_payment_term_id.line_ids
                        term_day = 0
                        for pay in pay_term:
                            term_day = pay.days
                            break 
                        due_date = invoice.invoice_date + relativedelta(days=term_day)
                        if due_date:
                            if due_date < record.payment_date:
                                # for payment in invoice.payment_ids.filtered(lambda x: x.id == record.id):
                                # for lines in invoice.invoice_line_ids:
                                #     line_total += lines.price_subtotal
                                if invoice.amount_total <= record.amount:
                                    # amount = line_total
                                    amount = invoice.amount_total
                                elif invoice.amount_total > record.amount:
                                    amount = record.amount
                                else:
                                    amount = 0
                record.arrears = amount

    @api.depends('current','arrears','amount')
    def _compute_advances(self):
        for record in self:
            amount_due = record.arrears + record.current
            if amount_due > 0 and record.amount > amount_due:
                record.advances = record.amount - amount_due
            else:
                record.advances = 0