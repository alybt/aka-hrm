from odoo import fields, models

class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    x_holiday_types = fields.Selection([
        ('regular', 'Regular Holiday'),
        ('special_non_working', 'Special Non-Working Day'),
        ('special_working', 'Special Working Day'),
        ('local', 'Local Holiday')
    ], string='PH Holiday Type', default='regular', help="Select the type of holiday for Philippine Payroll.")