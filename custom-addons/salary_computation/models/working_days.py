from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_working_days = fields.Float(
        string="Working Days (Excluding Holidays)",
        compute="_compute_working_days",
        store=True
    )

    x_overall_working_days = fields.Float(
        string="Working Days (Including Holidays)",
        compute="_compute_working_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_working_days(self):
        for rec in self:
            # Initialize both fields
            rec.x_working_days = 0
            rec.x_overall_working_days = 0

            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            # Get allowed weekdays from calendar
            allowed_weekdays = set(int(att.dayofweek) for att in calendar_res.attendance_ids)

            # Count total working days in the period (based on calendar)
            work_days_count = 0
            current = rec.date_from

            while current <= rec.date_to:
                if current.weekday() in allowed_weekdays:
                    work_days_count += 1
                current += timedelta(days=1)

            # Get holidays
            start_dt = datetime.combine(rec.date_from, datetime.min.time())
            end_dt = datetime.combine(rec.date_to, datetime.max.time())

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(end_dt)),
                ('date_to', '>=', fields.Datetime.to_string(start_dt)),
            ])

            # Filter holidays where x_holiday_types is True
            holiday_days = sum(1 for h in holidays if h.x_holiday_types)

            # x_working_days = working days minus holidays
            rec.x_working_days = work_days_count - holiday_days

            # x_overall_working_days = working days including holidays (just the raw count)
            rec.x_overall_working_days = work_days_count
