from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    # Computed fields for undertime
    x_undertime_hrs = fields.Float(
        string='Undertime Hours',
        compute='_compute_undertime',
        store=True,
        help='Undertime Hours = (Actual Regular Day x 8) - Worked Regular Hours'
    )

    x_undertime_amount = fields.Float(
        string='Undertime Amount',
        compute='_compute_undertime',
        store=True,
        help='Undertime Amount = Undertime Hours x Daily Salary'
    )

    # Optional: Hourly rate field
    x_hourly_rate = fields.Float(
        string='Hourly Rate',
        compute='_compute_undertime',
        store=True,
        help='Daily Salary / 8 hours'
    )

    @api.depends('x_actual_regular_day', 'x_worked_regular_hours', 'x_salary_daily')
    def _compute_undertime(self):
        """
        Compute undertime hours and amount
        Formula:
        x_undertime_hrs = (x_actual_regular_day * 8) - x_worked_regular_hours
        x_undertime_amount = x_undertime_hrs * (x_salary_daily / 8)
        """
        for rec in self:
            # Calculate expected hours (days * 8 hours per day)
            expected_hours = (rec.x_actual_regular_day or 0) * 8
            worked_hours = rec.x_worked_regular_hours or 0

            # Calculate Undertime Hours (only if worked hours are less than expected)
            if worked_hours < expected_hours:
                rec.x_undertime_hrs = expected_hours - worked_hours
            else:
                rec.x_undertime_hrs = 0.0  # No undertime if worked >= expected

            # Calculate Hourly Rate
            if rec.x_salary_daily and rec.x_salary_daily > 0:
                rec.x_hourly_rate = rec.x_salary_daily / 8
            else:
                rec.x_hourly_rate = 0.0

            # Calculate Undertime Amount
            rec.x_undertime_amount = rec.x_undertime_hrs * rec.x_hourly_rate

    @api.constrains('x_actual_regular_day', 'x_worked_regular_hours', 'x_salary_daily')
    def _check_positive_values(self):
        """Validate all input values are positive"""
        for rec in self:
            if rec.x_actual_regular_day and rec.x_actual_regular_day < 0:
                raise ValidationError("Actual Regular Days cannot be negative!")
            if rec.x_worked_regular_hours and rec.x_worked_regular_hours < 0:
                raise ValidationError("Worked Regular Hours cannot be negative!")
            if rec.x_salary_daily and rec.x_salary_daily < 0:
                raise ValidationError("Daily Salary cannot be negative!")

    # @api.constrains('x_worked_regular_hours', 'x_actual_regular_day')
    # def _check_max_hours(self):
    #     """Warn if worked hours exceed expected hours"""
    #     for rec in self:
    #         expected_hours = (rec.x_actual_regular_day or 0) * 8
    #         worked_hours = rec.x_worked_regular_hours or 0
    #         if worked_hours > expected_hours:
    #             raise ValidationError("Worked hours cannot exceed expected hours (%s hours)!" % expected_hours)