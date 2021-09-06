from datetime import datetime
from odoo import http, fields, models

class AWBOdooRestAPI(models.Model):
  _inherit = 'sale.subscription'

  is_active = fields.Boolean(string="Is Subscription Active", default=False)
