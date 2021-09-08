from odoo import models, fields


class CustomLead(models.Model):
    _inherit = "crm.lead"

    opportunity_number = fields.Char('SF Opportunity Number')
    sf_type = fields.Selection([("New", "New"),
                                ("Upgrade", "Upgrade"),
                                ("Recontract", "Recontract"),
                                ("Downgrade", "Downgrade"),
                                ("Reconnection", "Reconnection"),
                                ("Convert", "Convert"),
                                ("Disconnected", "Disconnected"),
                                ("Pre-Termination", "Pre-Termination"),
                                ("Transfer", "Transfer")
                                ], string='Type')
    jo_sms_id_username = fields.Char('Username')
    jo_sms_id_password = fields.Char('Password')
