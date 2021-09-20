from odoo import api, fields, models, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)



class SubscriberLocation(models.Model):
	_inherit = 'subscriber.location'

	active_count = fields.Integer(compute='_compute_active_subs')
	disconnected_count = fields.Integer(compute='_compute_disconnected_subs')
	total_count = fields.Integer(compute='_compute_total_subs')

	@api.depends('subscription_ids')
	def _compute_active_subs(self):
		for rec in self:
			rec.active_count = 0
			active = 0
			for lines in rec.subscription_ids:
				if lines.stage_id.in_progress == True:
					active += 1
					rec.active_count = active


	@api.depends('subscription_ids')
	def _compute_disconnected_subs(self):
		for rec in self:
			rec.disconnected_count = 0
			disconnected = 0
			for lines in rec.subscription_ids:
				if lines.stage_id.closed == True:
					disconnected += 1
					rec.disconnected_count = disconnected

	@api.depends('active_count','disconnected_count')
	def _compute_total_subs(self):
		for rec in self:
			rec.total_count = rec.active_count + rec.disconnected_count

class SubscriptionStage(models.Model):
	_inherit = 'sale.subscription.stage'

	closed = fields.Boolean()