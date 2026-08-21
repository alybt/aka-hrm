# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResourceCalendarLeaves(models.Model):
    """
    Extend Public Holidays (resource.calendar.leaves) to add a Holiday Type
    classification field.
    """
    _inherit = 'resource.calendar.leaves'

    holiday_type = fields.Selection(
        selection=[
            ('regular', 'Regular Holiday'),
            ('special_non_working', 'Special Non-Working Day'),
            ('special_working', 'Special Working Day'),
            ('local', 'Local Holiday'),
        ],
        string='Holiday Type',
        default='regular',
        index=True,
        tracking=True,
        help=(
            "Classify this public holiday:\n"
            "• Regular Holiday - National rest days with full pay "
            "(e.g. New Year's Day, Christmas Day).\n"
            "• Special Non-Working Day - Employees are not required to work; "
            "compensation rules depend on company/CBA policy.\n"
            "• Special Working Day - A normally non-working day that has been "
            "declared a working day by official proclamation.\n"
            "• Local Holiday - City- or province-declared holiday that applies "
            "only to a specific locality."
        ),
    )

    holiday_type_badge = fields.Char(
        string='Type Badge',
        compute='_compute_holiday_type_badge',
        store=False,
    )

    @api.depends('holiday_type')
    def _compute_holiday_type_badge(self):
        labels = {
            'regular': 'Regular',
            'special_non_working': 'Special Non-Working',
            'special_working': 'Special Working',
            'local': 'Local',
        }
        for rec in self:
            rec.holiday_type_badge = labels.get(rec.holiday_type, '')
