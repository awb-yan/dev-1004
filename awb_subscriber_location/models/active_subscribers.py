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

class AccountMove(models.Model):
	_inherit = 'account.move'

	location_id = fields.Many2one('subscriber.location', compute='_compute_location')
	area_id = fields.Many2one('subscriber.location', related='location_id.location_id')
	cluster_id = fields.Many2one('subscriber.location', related='area_id.location_id')
	head_id = fields.Many2one('subscriber.location', related='cluster_id.location_id')

	zone_name = fields.Char(related='location_id.name')
	area_name = fields.Char(related='location_id.location_id.name')
	cluster_name = fields.Char(related='cluster_id.name')
	head_name = fields.Char(related='head_id.name')

	@api.depends('partner_id')
	def _compute_location(self):
		for rec in self:
			_logger.info("PRINT TEST")
			print('PRINT TEST')
			rec.location_id = []
			if rec.partner_id:
				if rec.partner_id.subscriber_location_id.location_type == 'zone':
					rec.location_id = rec.partner_id.subscriber_location_id
				else:
					rec.location_id = []

# for record in self:
#   if record.x_studio_subscription and record.x_studio_subscription.subscriber_location_id:
#     record['x_studio_location'] = record.x_studio_subscription.subscriber_location_id
#   elif record.purchase_id:
#     record['x_studio_location'] = record.purchase_id.x_studio_location


	@api.depends('location_id')
	def _compute_area(self):
		for rec in self:
			rec.area_id = []
			if rec.partner_id:
				if rec.location_id.location_type == 'area':
					rec.area_id = rec.partner_id.subscriber_location_id.location_id
				else:
					rec.area_id = []

	@api.depends('area_id')
	def _compute_cluster(self):
		for rec in self:
			rec.cluster_id = []
			if rec.area_id:
				if rec.area_id.location_type == 'cluster':
					rec.cluster_id = rec.area_id.location_id
				else:
					rec.cluster_id = []

	@api.depends('cluster_id')
	def _compute_head(self):
		for rec in self:
			rec.head_id = []
			if rec.cluster_id:
				if rec.cluster_id.location_type == 'head':
					rec.head_id = rec.cluster_id.location_id
				else:
					rec.head_id = []