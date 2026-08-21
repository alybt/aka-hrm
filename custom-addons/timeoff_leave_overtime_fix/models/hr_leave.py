from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # This is the correct field name that exists in Odoo 17
    overtime_id = fields.Many2one('hr.attendance.overtime', string='Extra Hours')

    # This is the correct computed field for overtime deductible
    overtime_deductible = fields.Boolean(
        compute='_compute_overtime_deductible',
        string='Overtime Deductible'
    )

    @api.depends('holiday_status_id')
    def _compute_overtime_deductible(self):
        """Compute whether this leave type is overtime deductible"""
        for leave in self:
            leave.overtime_deductible = (
                leave.holiday_status_id.overtime_deductible and
                leave.holiday_status_id.requires_allocation == 'no'
            )

    # If you need to show employee's total overtime, use this related field
    employee_total_overtime = fields.Float(
        related='employee_id.total_overtime',
        string='Employee Total Overtime',
        groups='base.group_user'
    )

    @api.constrains('overtime_deductible', 'number_of_hours')
    def _check_overtime_balance(self):
        """Validate overtime balance when leave is overtime deductible"""
        for leave in self:
            if leave.overtime_deductible and leave.number_of_hours > 0:
                if leave.number_of_hours > leave.employee_id.total_overtime:
                    raise ValidationError(
                        f'Employee does not have enough extra hours. '
                        f'Available: {leave.employee_id.total_overtime:.2f} hours, '
                        f'Requested: {leave.number_of_hours:.2f} hours'
                    )