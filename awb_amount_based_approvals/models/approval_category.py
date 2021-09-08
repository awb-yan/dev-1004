# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ApprovalType(models.Model):
    _inherit = 'approval.category'

    rule_ids = fields.Many2many('approval.rule', String='Rules')
    has_department = fields.Selection([('required', 'Required'),],
                                    # ('no', 'None')],
                                    default='required', 
                                    string="Department", 
                                    required=True)
    has_manager = fields.Selection([('required', 'Required'),],
                                # ('no', 'None')],
                                default='required', 
                                string="Manager", 
                                required=True)