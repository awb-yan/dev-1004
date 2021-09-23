
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

	@api.onchange('recurring_invoice')
	def onchange_subscription_template(self):
		for rec in self:
			if rec.recurring_invoice == True:
				keyword = 'month' #default for postpaid

				if rec.sf_plan_type.name == 'Prepaid':
					keyword = rec.default_code

				rec.subscription_template_id = self.env['sale.subscription.template'].search([('name','ilike',keyword)], limit=1)
			else:
				rec.subscription_template_id = False



class CustomProductCategory(models.Model):
	_inherit = 'product.category'

	category_type = fields.Selection([
		('cable', 'Cable'),
		('internet', 'Internet'),
		('bundled', 'Bundled'),
		('non_service', 'None Service')], string="Type")