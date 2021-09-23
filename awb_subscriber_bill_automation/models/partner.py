from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = "res.partner"

    def _portal_activation(self):
        args = [
            ['name','=', self.name],
            ['email','!=', False],
            ['customer_rank','>', 0]
        ]
        partners = self.env['res.partner'].search(args)

        for partner in partners:
            _logger.debug(f'Creation of User Portal: {partner.name}')
            if not partner.user_ids:
                data = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'in_portal': True
                }
                vals = [(0,0,data)]
                new_record = self.env['portal.wizard'].sudo().create({'user_ids':vals})
                new_record.user_ids.sudo().action_apply()
                _logger.debug(f'{partner.name} - Done Creation of User Portal')

    @api.model
    def create(self, vals):
        res = super(Partner,self).create(vals)
        res._portal_activation()
        return res