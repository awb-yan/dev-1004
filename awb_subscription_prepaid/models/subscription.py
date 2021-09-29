from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    plan_name = fields.Char(related='plan_type.name')

    start_datetime = fields.Datetime(string="Start Datetime")
    end_datetime = fields.Datetime(string="End Datetime")

    @api.onchange('stage_id')
    def _get_start_end_datetime(self):
        for rec in self:
            if rec.stage_id.name == 'In Progress':
                if rec.plan_type.name == 'Prepaid':
                    rec.start_datetime = fields.Datetime.now()
                    if rec.recurring_rule_boundary == 'limited':
                        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                        rec.end_datetime = fields.Datetime.from_string(rec.start_datetime) + relativedelta(**{
                        periods[rec.recurring_rule_type]: rec.template_id.recurring_rule_count * rec.template_id.recurring_interval})
