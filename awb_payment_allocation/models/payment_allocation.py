# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

class AccountPayment(models.Model):
	_inherit = 'account.payment'

	posting_date = fields.Datetime()
	payment_line_ids = fields.Many2many('payment.allocation.line',compute='_load_invoices')

	# def _load_invoices(self):
	# 	pal_ids = []
	# 	for rec in self:
	# 		pal = self.env['payment.allocation.line'].search([('payment_id','=',rec.id)])
	# 		pal_ids.append(pal)
	# 	return pal_ids

class PaymentAllocationLine(models.Model):
	_inherit = 'payment.allocation.line'
	
	invoice_total = fields.Monetary(related='invoice.amount_total')