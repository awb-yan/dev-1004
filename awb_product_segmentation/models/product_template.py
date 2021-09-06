
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    product_segmentation = fields.Selection([
        ('month_service','Monthly Service Fee'),
        ('device','Device Fee'),
        ('security_deposit','Security Deposit Fee'),
        ('others','Others')], string="Product Segmentation" ,tracking=True)
        

    @api.onchange('product_segmentation')
    def onchange_product_segmentation(self):
        for rec in self:
            if rec.product_segmentation == 'month_service':
                rec.recurring_invoice = True
            else:
                rec.recurring_invoice = False


class CustomProductCategory(models.Model):
    _inherit = 'product.category'

    category_type = fields.Selection([
        ('cable', 'Cable'),
        ('internet', 'Internet'),
        ('bundled', 'Bundled'),
        ('non_service', 'None Service')], string="Type")