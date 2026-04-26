from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_undertime_hours = fields.Float(
        string="Undertime Hours",
        compute="_compute_undertime",
        store=True,
        help="Total number of undertime hours (hours worked less than scheduled)"
    )
    
    x_undertime_minutes = fields.Float(
        string="Undertime Minutes",
        compute="_compute_undertime",
        store=True,
        help="Total number of undertime minutes"
    )
    
    x_undertime_days = fields.Float(
        string="Undertime Days",
        compute="_compute_undertime",
        store=True,
        help="Undertime hours converted to days"
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_undertime(self):
        for rec in self:
            rec.x_undertime_hours = 0
            rec.x_undertime_minutes = 0
            rec.x_undertime_days = 0
            
            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            # Get scheduled weekdays and working hours from calendar
            scheduled_weekdays = set()
            scheduled_hours_per_day = {}
            
            for att in calendar_res.attendance_ids:
                dayofweek = int(att.dayofweek)
                scheduled_weekdays.add(dayofweek)
                
                # Calculate scheduled hours for this day
                work_hours = self._calculate_work_hours(att)
                scheduled_hours_per_day[dayofweek] = work_hours

            # Calculate holidays
            start_dt = datetime.combine(rec.date_from, datetime.min.time())
            end_dt = datetime.combine(rec.date_to, datetime.max.time())

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(end_dt)),
                ('date_to', '>=', fields.Datetime.to_string(start_dt)),
            ])

            # Track holiday dates
            holiday_dates = set()
            for holiday in holidays:
                if not holiday.x_holiday_types:
                    continue
                    
                holiday_start = holiday.date_from.date()
                holiday_end = holiday.date_to.date()
                
                holiday_current = holiday_start
                while holiday_current <= holiday_end:
                    if holiday_current >= rec.date_from and holiday_current <= rec.date_to:
                        if holiday_current.weekday() in scheduled_weekdays:
                            holiday_dates.add(holiday_current)
                    holiday_current += timedelta(days=1)

            # Get actual attendance records
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
            ])
            
            total_undertime_minutes = 0
            
            # Group attendances by date
            attendance_by_date = {}
            for attendance in attendances:
                attendance_date = attendance.check_in.date()
                if attendance_date not in attendance_by_date:
                    attendance_by_date[attendance_date] = []
                attendance_by_date[attendance_date].append(attendance)
            
            # Calculate undertime for each attended day (excluding holidays)
            for date, daily_attendances in attendance_by_date.items():
                # Skip if not a scheduled working day
                if date.weekday() not in scheduled_weekdays:
                    continue
                
                # Skip if it's a holiday
                if date in holiday_dates:
                    continue
                
                # Skip if employee was absent (no check_out)
                has_complete_attendance = any(a.check_out for a in daily_attendances)
                if not has_complete_attendance:
                    continue
                
                # Calculate total actual hours worked for this day in minutes
                actual_minutes = 0
                for attendance in daily_attendances:
                    if attendance.check_in and attendance.check_out:
                        duration = attendance.check_out - attendance.check_in
                        actual_minutes += duration.total_seconds() / 60.0
                
                # Get scheduled hours for this day in minutes
                scheduled_hours = scheduled_hours_per_day.get(date.weekday(), 0)
                scheduled_minutes = scheduled_hours * 60
                
                # Calculate undertime for this day (only if less than scheduled)
                if actual_minutes < scheduled_minutes:
                    undertime_today = scheduled_minutes - actual_minutes
                    total_undertime_minutes += undertime_today
            
            # Set undertime values
            rec.x_undertime_minutes = total_undertime_minutes
            rec.x_undertime_hours = total_undertime_minutes / 60.0
            
            # Convert undertime hours to days (based on standard working hours)
            if scheduled_hours_per_day:
                avg_working_hours = sum(scheduled_hours_per_day.values()) / len(scheduled_hours_per_day)
                if avg_working_hours > 0:
                    rec.x_undertime_days = rec.x_undertime_hours / avg_working_hours
                else:
                    rec.x_undertime_days = 0
            else:
                rec.x_undertime_days = 0
    
    def _calculate_work_hours(self, attendance):
        """Calculate total working hours for an attendance record"""
        if attendance.work_entry_type_id:
            # If using work entries
            return attendance.work_entry_type_id.duration / 60.0 if attendance.work_entry_type_id.duration else 0
        
        # Calculate from attendance times
        if attendance.hour_from and attendance.hour_to:
            hours = attendance.hour_to - attendance.hour_from
            return hours
        
        return 0