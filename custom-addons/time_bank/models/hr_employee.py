from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_time_bank = fields.Float(
        string='Time Bank Balance',
        default=0.0
    )