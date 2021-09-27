# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ProductPlanType(models.Model):
    _name = 'product.plan.type'
    _description = 'Plan Type'

    name = fields.Char('Name', required=True, tracking=True)
    description = fields.Text('Description')

class ProductFacilityType(models.Model):
    _name = 'product.facility.type'
    _description = 'Facility Type'

    name = fields.Char('Name', required=True, tracking=True)
    description = fields.Text('Description', tracking=True)
    is_aradial_product = fields.Boolean('Aradial Product', default=False, tracking=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sf_plan_type = fields.Many2one('product.plan.type', string="Plan Type", tracking=True)
    sf_facility_type = fields.Many2one('product.facility.type', string="Facility Type", tracking=True)

class CustomResPartner(models.Model):
    _inherit = 'res.partner'

    plan_type = fields.Many2one('product.plan.type', compute='_compute_plan_type')

    @api.depends('opportunity_count')
    def _compute_plan_type(self):
        for rec in self:
            plan_type_id = []
            for line in rec.opportunity_ids:
                for x in line.product_lines:
                    if line.product_lines:
                        plan_type_id = x.product_id.sf_plan_type
                    else:
                        plan_type_id = []

            rec.plan_type = plan_type_id
