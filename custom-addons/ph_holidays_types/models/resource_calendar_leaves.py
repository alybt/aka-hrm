from odoo import fields, models

class ResourceCalendarLeave(models.Model):
    _inherit = 'resource.calendar.leaves'

    holiday_type = fields.Selection([
        ('regular', 'Regular Holiday'),
        ('special_non_working', 'Special Non-Working Holiday'),
        ('special_working', 'Special Working Holiday'),
        ('local', 'Local Holiday')
    ], 
        string = 'PH Holiday Type',
        default = 'regular',
        help = "Categorization for Philippine Labor Law Compliance."
    )