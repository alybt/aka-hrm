from odoo import api, fields, models, _

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    
    def _get_absence_deduction(self, payslip, employees, date_from, date_to):
        """Compute absence deduction amount"""
        result = 0.0
        for employee in employees:
            # Calculate absences for the period
            absence_data = payslip._calculate_absences_for_period(employee, date_from, date_to)
            
            # Get daily rate (you can customize this based on your salary structure)
            contract = employee.contract_id
            if contract and contract.wage:
                working_days_in_month = 26  # Standard working days, adjust as needed
                daily_rate = contract.wage / working_days_in_month
                absence_deduction = absence_data['absence_days'] * daily_rate
                result += absence_deduction
        
        return result
    
    def _get_attendance_bonus(self, payslip, employees, date_from, date_to):
        """Compute attendance bonus based on perfect attendance"""
        result = 0.0
        for employee in employees:
            absence_data = payslip._calculate_absences_for_period(employee, date_from, date_to)
            
            # If no absences and no holidays (or holidays don't count against attendance)
            if absence_data['absence_days'] == 0:
                # You can set a fixed attendance bonus amount
                attendance_bonus = 1000.0  # Example amount
                result += attendance_bonus
        
        return result