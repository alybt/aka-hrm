from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if not self.employee_ids:
            return
            
        active_id = self.env.context.get('active_id')
        if not active_id:
            return
            
        run_data = self.env['hr.payslip.run'].browse(active_id)
        from_date = run_data.date_start
        
        if not from_date:
            return
            
        month = from_date.month
        year = from_date.year
        
        # Check for employees who already have a payslip in this month
        duplicate_employees = []
        duplicate_employee_ids = []
        domain = [
            ('employee_id', 'in', self.employee_ids.ids),
            ('state', '!=', 'cancel'),
        ]
        existing_payslips = self.env['hr.payslip'].search(domain)
        for existing in existing_payslips:
            if existing.date_from and existing.date_from.month == month and existing.date_from.year == year:
                if existing.employee_id.name not in duplicate_employees:
                    duplicate_employees.append(existing.employee_id.name)
                    duplicate_employee_ids.append(existing.employee_id.id)
                    
        if duplicate_employees:
            # Deselect the employees that already have a payslip
            self.employee_ids = self.employee_ids.filtered(lambda e: e.id not in duplicate_employee_ids)
            
            employee_names = ", ".join(duplicate_employees)
            return {
                'warning': {
                    'title': _("Duplicate Month Validation"),
                    'message': _("The following employee(s) already have a payslip for the month of %(month)02d/%(year)d and have been deselected:\n\n%(employees)s") % {
                        'month': month,
                        'year': year,
                        'employees': employee_names
                    }
                }
            }
