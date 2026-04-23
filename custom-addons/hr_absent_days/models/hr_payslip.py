from odoo import models, fields, api
from datetime import timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_absent_days = fields.Float(
        string="Absent Days",
        compute="_compute_absent_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_absent_days(self):
        for slip in self:
            absent_days = 0
            
            if not slip.date_from or not slip.date_to or not slip.employee_id:
                slip.x_absent_days = 0
                continue
            
            current_date = slip.date_from
            while current_date <= slip.date_to:
                # Check if the day is a working day
                if self._is_working_day(slip.contract_id.resource_calendar_id, current_date):
                    # Check for attendance on this day
                    attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', slip.employee_id.id),
                        ('check_in', '>=', current_date),
                        ('check_in', '<', current_date + timedelta(days=1))
                    ])
                    
                    if not attendances:
                        # No attendance at all
                        absent_days += 1
                    else:
                        # Check if any attendance has WORK100 (or your specific work code)
                        has_work100 = False
                        for attendance in attendances:
                            # Assuming you have a field for work code in hr.attendance
                            # Adjust field name as per your actual field name (e.g., work_code, work_type, etc.)
                            if hasattr(attendance, 'work_code') and attendance.work_code == 'WORK100':
                                has_work100 = True
                                break
                            # Or check via related fields if work code is elsewhere
                        
                        if not has_work100:
                            absent_days += 1
                
                current_date += timedelta(days=1)
            
            slip.x_absent_days = absent_days

    def _is_working_day(self, calendar, date):
        """Check if a specific date is a working day based on the resource calendar"""
        if not calendar:
            return True  # If no calendar, assume all days are working days
        
        # Get working hours for the specific date
        intervals = calendar._get_work_intervals(date, date + timedelta(days=1))
        return len(intervals) > 0