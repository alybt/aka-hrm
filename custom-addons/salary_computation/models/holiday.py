from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_hrly_regular_holiday = fields.Float(
        string='Hourly Regular Holiday Rate',
        compute='_compute_holiday_rates',
        store=True,
        help='(Daily Salary / 8) * 200% if worked, else 100%'
    )

    x_hrly_specialnw_holiday = fields.Float(
        string='Hourly Special Non-Working Holiday Rate',
        compute='_compute_holiday_rates',
        store=True,
        help='(Daily Salary / 8) * 130% if worked, else 0'
    )

    x_hrly_specialw_holiday = fields.Float(
        string='Hourly Special Working Holiday Rate',
        compute='_compute_holiday_rates',
        store=True,
        help='(Daily Salary / 8) * 100% if worked, else 0'
    )

    # Total pay fields
    x_total_regular_holiday_pay = fields.Float(
        string='Total Regular Holiday Pay',
        compute='_compute_total_pay',
        store=True,
    )

    x_total_specialnw_holiday_pay = fields.Float(
        string='Total Special Non-Working Pay',
        compute='_compute_total_pay',
        store=True,
    )

    x_total_specialw_holiday_pay = fields.Float(
        string='Total Special Working Pay',
        compute='_compute_total_pay',
        store=True,
    )

    x_total_holiday_pay = fields.Float(
        string='Total Holiday Pay',
        compute='_compute_total_pay',
        store=True,
    )

    @api.depends('x_salary_daily', 'x_actual_regular_holiday', 'x_worked_regular_holiday_hours',
                    'x_actual_specialnw_holiday', 'x_worked_specialnw_holiday_hours',
                    'x_actual_specialw_holiday', 'x_worked_specialw_holiday_hours')
    def _compute_holiday_rates(self):
        """
        Compute hourly rates for different holiday types
        Formula: Hourly Rate = (Daily Salary / 8 hours per day)
        """
        for payslip in self:
            # 1. Calculate hourly rate
            hourly_rate = (payslip.x_salary_daily / 8) if (payslip.x_salary_daily or 0) > 0 else 0

            # 2. Regular Holiday Logic
            # If a holiday exists, we need to determine the rate
            if payslip.x_actual_regular_holiday:
                # Check if they worked the full day (8 hours per holiday day)
                if payslip.x_worked_regular_holiday_hours == (payslip.x_actual_regular_holiday * 8):
                    payslip.x_hrly_regular_holiday = hourly_rate * 2.0  # Worked: 200%
                else:
                    payslip.x_hrly_regular_holiday = hourly_rate * 1.0  # Did not work/Partial: 100%
            else:
                payslip.x_hrly_regular_holiday = 0

            # 3. Special Non-Working Holiday (130% if worked, else 0)
            if payslip.x_actual_specialnw_holiday and payslip.x_worked_specialnw_holiday_hours > 0:
                payslip.x_hrly_specialnw_holiday = hourly_rate * 1.3
            else:
                payslip.x_hrly_specialnw_holiday = 0

            # 4. Special Working Holiday (100% if worked, else 0)
            if payslip.x_actual_specialw_holiday and payslip.x_worked_specialw_holiday_hours > 0:
                payslip.x_hrly_specialw_holiday = hourly_rate * 1.0
            else:
                payslip.x_hrly_specialw_holiday = 0

    @api.depends('x_hrly_regular_holiday', 'x_actual_regular_holiday', 'x_worked_regular_holiday_hours',
                    'x_salary_daily',
                    'x_hrly_specialnw_holiday', 'x_actual_specialnw_holiday',
                    'x_hrly_specialw_holiday', 'x_actual_specialw_holiday')
    def _compute_total_pay(self):
        """
        Compute total pay for each holiday type
        Total Pay = Hourly Rate × Hours Worked
        """
        for payslip in self:
            # Regular Holiday Total Pay
            regular_expected_hours = (payslip.x_actual_regular_holiday or 0) * 8
            regular_worked_hours = payslip.x_worked_regular_holiday_hours or 0

            if 0 < regular_worked_hours < regular_expected_hours:
                # Undertime: (Hourly Rate × Worked Hours) + (Daily Salary × Number of Days)
                payslip.x_total_regular_holiday_pay = (payslip.x_hrly_regular_holiday * regular_worked_hours) + (payslip.x_salary_daily * (payslip.x_actual_regular_holiday or 0))
            else:
                # Full work or no work: Hourly Rate × Expected Hours
                payslip.x_total_regular_holiday_pay = payslip.x_hrly_regular_holiday * regular_expected_hours

            # Special Non-Working Total Pay
            specialnw_hours = payslip.x_actual_specialnw_holiday or 0
            payslip.x_total_specialnw_holiday_pay = payslip.x_hrly_specialnw_holiday * specialnw_hours

            # Special Working Total Pay
            specialw_hours = payslip.x_actual_specialw_holiday or 0
            payslip.x_total_specialw_holiday_pay = payslip.x_hrly_specialw_holiday * specialw_hours

            # Total Holiday Pay (sum of all)
            payslip.x_total_holiday_pay = (payslip.x_total_regular_holiday_pay +
                                            payslip.x_total_specialnw_holiday_pay +
                                            payslip.x_total_specialw_holiday_pay)

    @api.constrains('x_salary_daily')
    def _check_daily_salary(self):
        """Validate daily salary is positive"""
        for payslip in self:
            if payslip.x_salary_daily and payslip.x_salary_daily < 0:
                raise ValidationError("Daily salary cannot be negative!")

    @api.constrains('x_actual_regular_holiday', 'x_actual_specialnw_holiday', 'x_actual_specialw_holiday')
    def _check_actual_hours(self):
        """Validate actual hours are not negative"""
        for payslip in self:
            if payslip.x_actual_regular_holiday and payslip.x_actual_regular_holiday < 0:
                raise ValidationError("Actual Regular Holiday days cannot be negative!")
            if payslip.x_actual_specialnw_holiday and payslip.x_actual_specialnw_holiday < 0:
                raise ValidationError("Actual Special Non-Working Holiday hours cannot be negative!")
            if payslip.x_actual_specialw_holiday and payslip.x_actual_specialw_holiday < 0:
                raise ValidationError("Actual Special Working Holiday hours cannot be negative!")