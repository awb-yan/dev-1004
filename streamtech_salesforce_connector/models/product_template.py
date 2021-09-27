# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     sf_plan_type = fields.Many2one('product.plan.type', string="Plan Type", tracking=True)
#     sf_facility_type = fields.Many2one('product.facility.type', string="Facility Type", tracking=True)
    

# class ProductPlanType(models.Model):
#     _name = 'product.plan.type'
#     _description = 'Plan Type'

#     name = fields.Char('Name', required=True, tracking=True)
#     description = fields.Text('Description')

# access_sale_product_facility_type,product.facility.type,model_product_facility_type,sales_team.group_sale_salesman,1,0,0,0
# access_sale_product_facility_type_manager,product.facility.type manager,model_product_facility_type,sales_team.group_sale_manager,1,1,1,1
# access_sale_product_plan_type,product.plan.type,model_product_plan_type,sales_team.group_sale_salesman,1,0,0,0
# access_sale_product_plan_type_manager,product.plan.type manager,model_product_plan_type,sales_team.group_sale_manager,1,1,1,1


# class ProductFacilityType(models.Model):
#     _name = 'product.facility.type'
#     _description = 'Facility Type'

#     name = fields.Char('Name', required=True, tracking=True)
#     description = fields.Text('Description', tracking=True)
#     is_aradial_product = fields.Boolean('Aradial Product', default=False, tracking=True)