from odoo import fields, models


class HrHolidaysPublicLine(models.Model):
    _inherit = "hr.holidays.public.line"

    holiday_type = fields.Selection([
        ('regular', 'Regular Holiday'),
        ('special_non_working', 'Special Non-Working Holiday'),
        ('special_working', 'Special Working Holiday'),
        ('local', 'Local Holiday'),
    ], string="Holiday Type", default='regular', required=True)