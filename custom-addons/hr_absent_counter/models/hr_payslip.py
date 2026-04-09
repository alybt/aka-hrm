from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    total_absence_days = fields.Float(
        string='Total Absence Days (Excluding Holidays)',
        compute='_compute_absence_details',
        store=True,
        help="Total absence days excluding configured holidays"
    )
    total_holiday_days = fields.Float(
        string='Total Holiday Days',
        compute='_compute_absence_details',
        store=True,
        help="Total holiday days excluded from absence"
    )
    total_working_days_period = fields.Float(
        string='Working Days in Period',
        compute='_compute_absence_details',
        store=True,
        help="Total working days in payslip period"
    )
    absence_details_ids = fields.One2many(
        'hr.payslip.absence.detail',
        'payslip_id',
        string='Absence Details'
    )
    
    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_absence_details(self):
        """Compute absence details for payslip period"""
        for payslip in self:
            if payslip.employee_id and payslip.date_from and payslip.date_to:
                absence_data = self._calculate_absences_for_period(
                    payslip.employee_id,
                    payslip.date_from,
                    payslip.date_to
                )
                payslip.total_working_days_period = absence_data['working_days']
                payslip.total_holiday_days = absence_data['holiday_days']
                payslip.total_absence_days = absence_data['absence_days']
                
                # Create absence details records
                payslip._create_absence_details(absence_data['absence_records'])
            else:
                payslip.total_working_days_period = 0
                payslip.total_holiday_days = 0
                payslip.total_absence_days = 0
    
    def _calculate_absences_for_period(self, employee, date_from, date_to):
        """Calculate absences excluding holidays for a given period"""
        # Get work schedule
        work_schedule = self._get_employee_work_schedule(employee)
        
        # Get all days in period
        all_days = self._get_days_in_range(date_from, date_to)
        
        # Get holidays from resource.calendar.leaves with holiday types
        holidays = self._get_holidays_in_range(date_from, date_to)
        
        # Get time off/leaves for employee
        time_off_days = self._get_time_off_days(employee, date_from, date_to)
        
        # Calculate statistics
        working_days_count = 0.0
        holiday_days_count = 0.0
        absence_days_count = 0.0
        absence_records = []
        
        for day in all_days:
            if self._is_working_day(day, work_schedule):
                working_days_count += 1.0
                
                # Check if day is a holiday
                holiday = next((h for h in holidays if h.date_from.date() <= day.date() <= h.date_to.date()), None)
                
                if holiday:
                    holiday_days_count += 1.0
                    # Still record but marked as holiday (not counted as absence)
                    absence_records.append({
                        'date': day.date(),
                        'day_type': 'holiday',
                        'holiday_name': holiday.name,
                        'holiday_type': dict(holiday._fields['x_holiday_types'].selection).get(holiday.x_holiday_types),
                        'absence_days': 0.0,
                    })
                else:
                    # Check if employee was absent
                    leave = next((l for l in time_off_days if l.date_from.date() <= day.date() <= l.date_to.date()), None)
                    if leave:
                        absence_days_count += 1.0
                        absence_records.append({
                            'date': day.date(),
                            'day_type': 'absent',
                            'leave_id': leave.id,
                            'leave_type': leave.holiday_status_id.name,
                            'absence_days': 1.0,
                        })
                    else:
                        absence_records.append({
                            'date': day.date(),
                            'day_type': 'present',
                            'absence_days': 0.0,
                        })
        
        return {
            'working_days': working_days_count,
            'holiday_days': holiday_days_count,
            'absence_days': absence_days_count,
            'absence_records': absence_records,
        }
    
    def _create_absence_details(self, absence_records):
        """Create absence detail records for payslip"""
        # Clear existing details
        self.absence_details_ids.unlink()
        
        for record in absence_records:
            self.env['hr.payslip.absence.detail'].create({
                'payslip_id': self.id,
                'date': record['date'],
                'day_type': record['day_type'],
                'holiday_name': record.get('holiday_name'),
                'holiday_type': record.get('holiday_type'),
                'leave_id': record.get('leave_id'),
                'leave_type': record.get('leave_type'),
                'absence_days': record.get('absence_days', 0.0),
            })
    
    def _get_employee_work_schedule(self, employee):
        """Get employee's work schedule"""
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
    
    def _get_holidays_in_range(self, date_from, date_to):
        """Get holidays from resource.calendar.leaves"""
        return self.env['resource.calendar.leaves'].search([
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('x_holiday_types', 'in', ['regular', 'special_non_working', 'special_working', 'local'])
        ])
    
    def _get_time_off_days(self, employee, date_from, date_to):
        """Get time off days for employee"""
        return self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('state', '=', 'validate')
        ])
    
    def _is_working_day(self, date, calendar):
        """Check if day is a working day"""
        if calendar:
            working_hours = calendar.attendee_ids.filtered(
                lambda a: a.dayofweek == str(date.weekday())
            )
            return bool(working_hours)
        return date.weekday() < 5
    
    def get_absence_deduction_amount(self, daily_rate):
        """Calculate absence deduction amount"""
        self.ensure_one()
        return self.total_absence_days * daily_rate
    
    def get_attendance_days_for_salary(self):
        """Get actual attendance days for salary computation"""
        self.ensure_one()
        return self.total_working_days_period - self.total_holiday_days - self.total_absence_days


class HrPayslipAbsenceDetail(models.Model):
    _name = 'hr.payslip.absence.detail'
    _description = 'Payslip Absence Detail'
    _order = 'date'
    
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True)
    day_type = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('holiday', 'Holiday')
    ], string='Day Type', required=True)
    holiday_name = fields.Char(string='Holiday Name')
    holiday_type = fields.Char(string='Holiday Type')
    leave_id = fields.Many2one('hr.leave', string='Leave Request')
    leave_type = fields.Char(string='Leave Type')
    absence_days = fields.Float(string='Absence Days', default=0.0)