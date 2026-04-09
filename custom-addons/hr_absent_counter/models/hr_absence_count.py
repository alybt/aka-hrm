from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class HRAbsenceCount(models.TransientModel):
    _name = 'hr.absence.count'
    _description = 'HR Absence Count Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date(string='Start Date', required=True, 
                            default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='End Date', required=True,
                            default=lambda self: fields.Date.today())
    
    absence_days = fields.Float(string='Absence Days (Excluding Holidays)', compute='_compute_absence_days')
    holiday_days = fields.Float(string='Holiday Days (Excluded)', compute='_compute_absence_days')
    working_days = fields.Float(string='Total Working Days', compute='_compute_absence_days')
    attendance_days = fields.Float(string='Actual Attendance Days', compute='_compute_absence_days')
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_absence_days(self):
        for record in self:
            if record.employee_id and record.date_from and record.date_to:
                result = record._count_absences_excluding_holidays()
                record.absence_days = result['absence_days']
                record.holiday_days = result['holiday_days']
                record.working_days = result['working_days']
                record.attendance_days = result['attendance_days']
    
    def _count_absences_excluding_holidays(self):
        """Count absences while excluding holiday types from resource.calendar.leaves"""
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        
        # Get work schedule for employee
        work_schedule = self._get_employee_work_schedule(employee)
        
        # Get all days in range
        all_days = self._get_days_in_range(date_from, date_to)
        
        # Get holidays from resource.calendar.leaves with holiday types
        holidays = self._get_holidays_from_calendar_leaves(date_from, date_to)
        
        # Get time off/leaves from hr.leave
        time_off_days = self._get_time_off_days(employee, date_from, date_to)
        
        # Calculate statistics
        working_days_count = 0.0
        holiday_days_count = 0.0
        absence_days_count = 0.0
        
        for day in all_days:
            if self._is_working_day(day, work_schedule):
                working_days_count += 1.0
                
                # Check if day is a holiday (excluded from absence counting)
                is_holiday = any(h for h in holidays if h.date_from.date() <= day.date() <= h.date_to.date())
                
                if is_holiday:
                    holiday_days_count += 1.0
                else:
                    # Check if employee was absent (has time off)
                    day_off = next((to for to in time_off_days if to.date_from.date() <= day.date() <= to.date_to.date()), None)
                    if day_off:
                        absence_days_count += self._calculate_absence_duration(day_off, day.date())
        
        attendance_days_count = working_days_count - holiday_days_count - absence_days_count
        
        return {
            'working_days': working_days_count,
            'holiday_days': holiday_days_count,
            'absence_days': absence_days_count,
            'attendance_days': attendance_days_count,
        }
    
    def _get_employee_work_schedule(self, employee):
        """Get employee's work schedule from contract"""
        contract = employee.contract_id
        if contract and contract.resource_calendar_id:
            return contract.resource_calendar_id
        return self.env.company.resource_calendar_id
    
    def _get_days_in_range(self, date_from, date_to):
        """Get all days between two dates"""
        days = []
        current_date = date_from
        while current_date <= date_to:
            days.append(current_date)
            current_date += timedelta(days=1)
        return days
    
    def _get_holidays_from_calendar_leaves(self, date_from, date_to):
        """Get holidays from resource.calendar.leaves that have PH Holiday Types"""
        # Get all holidays in the date range that have x_holiday_types set
        holidays = self.env['resource.calendar.leaves'].search([
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
            ('x_holiday_types', 'in', ['regular', 'special_non_working', 'special_working', 'local'])
        ])
        
        # Also check for holidays that might span across the date boundaries
        overlapping_holidays = self.env['resource.calendar.leaves'].search([
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('x_holiday_types', 'in', ['regular', 'special_non_working', 'special_working', 'local'])
        ])
        
        return holidays | overlapping_holidays
    
    def _get_time_off_days(self, employee, date_from, date_to):
        """Get all time off/leave days for employee"""
        return self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('state', '=', 'validate')
        ])
    
    def _is_working_day(self, date, calendar):
        """Check if a day is a working day based on employee's calendar"""
        if calendar:
            # Check if day is in calendar's working hours
            working_hours = calendar.attendee_ids.filtered(
                lambda a: a.dayofweek == str(date.weekday())
            )
            return bool(working_hours)
        # Default: Monday to Friday are working days
        return date.weekday() < 5
    
    def _calculate_absence_duration(self, leave, date):
        """Calculate absence duration for a specific day"""
        if leave.date_from.date() == leave.date_to.date():
            # Single day leave
            return leave.number_of_days
        else:
            # Multi-day leave, calculate portion for this specific day
            # Assuming full day absence if the date falls within the leave range
            return 1.0
    
    def action_generate_report(self):
        """Generate absence report"""
        # Create report record
        report = self.env['hr.absence.report'].create({
            'employee_id': self.employee_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'working_days': self.working_days,
            'holiday_days': self.holiday_days,
            'absence_days': self.absence_days,
            'attendance_days': self.attendance_days,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Absence Report',
            'res_model': 'hr.absence.report',
            'res_id': report.id,
            'view_mode': 'form',
            'target': 'current',
        }


class HRAbsenceReport(models.Model):
    _name = 'hr.absence.report'
    _description = 'HR Absence Report'
    _order = 'create_date desc'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    working_days = fields.Float(string='Total Working Days')
    holiday_days = fields.Float(string='Holiday Days (Excluded)')
    absence_days = fields.Float(string='Absence Days')
    attendance_days = fields.Float(string='Actual Attendance Days')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    create_date = fields.Datetime(string='Created Date', readonly=True)
    
    def action_view_details(self):
        """View detailed absence breakdown"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Absence Details - {self.employee_id.name}',
            'res_model': 'hr.absence.detail',
            'view_mode': 'tree,form',
            'domain': [('report_id', '=', self.id)],
            'target': 'current',
        }


class HRAbsenceDetail(models.TransientModel):
    _name = 'hr.absence.detail'
    _description = 'HR Absence Detail'
    
    report_id = fields.Many2one('hr.absence.report', string='Report')
    date = fields.Date(string='Date')
    day_type = fields.Selection([
        ('working', 'Working Day'),
        ('holiday', 'Holiday'),
        ('absent', 'Absent'),
        ('attended', 'Attended')
    ], string='Day Type')
    leave_id = fields.Many2one('hr.leave', string='Leave Request')
    holiday_type = fields.Char(string='Holiday Type')
    
    def action_view_details(self):
        """Generate detailed day-by-day breakdown"""
        report = self.report_id
        employee = report.employee_id
        date_from = report.date_from
        date_to = report.date_to
        
        # Clear existing details
        self.search([('report_id', '=', report.id)]).unlink()
        
        # Get work schedule
        work_schedule = self._get_employee_work_schedule(employee)
        
        # Get holidays
        holidays = self._get_holidays_from_calendar_leaves(date_from, date_to)
        
        # Get time off
        time_off = self._get_time_off_days(employee, date_from, date_to)
        
        # Analyze each day
        current_date = date_from
        while current_date <= date_to:
            day_type = 'working'
            holiday_type = False
            leave_id = False
            
            # Check if working day
            if self._is_working_day(current_date, work_schedule):
                # Check if holiday
                holiday = next((h for h in holidays if h.date_from.date() <= current_date <= h.date_to.date()), None)
                if holiday:
                    day_type = 'holiday'
                    holiday_type = dict(holiday._fields['x_holiday_types'].selection).get(holiday.x_holiday_types)
                else:
                    # Check if absent
                    leave = next((l for l in time_off if l.date_from.date() <= current_date <= l.date_to.date()), None)
                    if leave:
                        day_type = 'absent'
                        leave_id = leave.id
                    else:
                        day_type = 'attended'
            else:
                day_type = 'working'  # Non-working days are not counted
            
            # Create detail record
            self.create({
                'report_id': report.id,
                'date': current_date,
                'day_type': day_type,
                'leave_id': leave_id,
                'holiday_type': holiday_type,
            })
            
            current_date += timedelta(days=1)
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Detailed Absence Breakdown - {employee.name}',
            'res_model': 'hr.absence.detail',
            'view_mode': 'tree,form',
            'domain': [('report_id', '=', report.id)],
            'target': 'current',
        }
    
    def _get_employee_work_schedule(self, employee):
        """Get employee's work schedule"""
        contract = employee.contract_id
        if contract and contract.resource_calendar_id:
            return contract.resource_calendar_id
        return self.env.company.resource_calendar_id
    
    def _get_holidays_from_calendar_leaves(self, date_from, date_to):
        """Get holidays from resource.calendar.leaves"""
        return self.env['resource.calendar.leaves'].search([
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('x_holiday_types', 'in', ['regular', 'special_non_working', 'special_working', 'local'])
        ])
    
    def _get_time_off_days(self, employee, date_from, date_to):
        """Get time off days"""
        return self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('state', '=', 'validate')
        ])
    
    def _is_working_day(self, date, calendar):
        """Check if working day"""
        if calendar:
            working_hours = calendar.attendee_ids.filtered(
                lambda a: a.dayofweek == str(date.weekday())
            )
            return bool(working_hours)
        return date.weekday() < 5