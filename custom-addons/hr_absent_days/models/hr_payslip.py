from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_absent_days = fields.Float(
        string="Absent Days",
        compute="_compute_absent_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_absent_days(self):
        for rec in self:
            rec.x_absent_days = 0
            
            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            # Get scheduled weekdays from calendar (days they should work)
            scheduled_weekdays = set(int(att.dayofweek) for att in calendar_res.attendance_ids)

            # Count scheduled working days in the period
            scheduled_days_count = 0
            scheduled_dates = []
            current = rec.date_from
            
            while current <= rec.date_to:
                if current.weekday() in scheduled_weekdays:
                    scheduled_days_count += 1
                    scheduled_dates.append(current)
                current += timedelta(days=1)

            # Calculate holidays (days they're exempted from work)
            start_dt = datetime.combine(rec.date_from, datetime.min.time())
            end_dt = datetime.combine(rec.date_to, datetime.max.time())

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(end_dt)),
                ('date_to', '>=', fields.Datetime.to_string(start_dt)),
            ])

            # Count holiday days that fall on scheduled working days
            holiday_dates = set()
            for holiday in holidays:
                if not holiday.x_holiday_types:
                    continue
                    
                holiday_start = holiday.date_from.date()
                holiday_end = holiday.date_to.date()
                
                holiday_current = holiday_start
                while holiday_current <= holiday_end:
                    # Only count if it's a scheduled working day and within period
                    if holiday_current >= rec.date_from and holiday_current <= rec.date_to:
                        if holiday_current.weekday() in scheduled_weekdays:
                            holiday_dates.add(holiday_current)
                    holiday_current += timedelta(days=1)

            # Get actual attendance records for the employee in this period
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
            ])
            
            # Count unique days the employee actually worked/attended
            attended_dates = set()
            for attendance in attendances:
                attendance_date = attendance.check_in.date()
                # Check if it's a scheduled working day
                if attendance_date >= rec.date_from and attendance_date <= rec.date_to:
                    if attendance_date.weekday() in scheduled_weekdays:
                        attended_dates.add(attendance_date)
            
            working_days_after_holidays = scheduled_days_count - len(holiday_dates)
            
            # Absent days = (Working days after holidays) - (Days actually attended)
            rec.x_absent_days = working_days_after_holidays - len(attended_dates)
            
            # Ensure we don't have negative absent days
            if rec.x_absent_days < 0:
                rec.x_absent_days = 0