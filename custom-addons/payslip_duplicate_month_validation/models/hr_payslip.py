from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.constrains('employee_id', 'date_from', 'state')
    def _check_duplicate_month(self):
        for payslip in self:
            if payslip.state == 'cancel':
                continue
                
            if payslip.employee_id and payslip.date_from:
                month = payslip.date_from.month
                year = payslip.date_from.year
                
                # Check for existing payslips for the same employee in the same month/year
                domain = [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('id', '!=', payslip.id),
                    ('state', '!=', 'cancel'),
                ]
                
                existing_payslips = self.search(domain)
                for existing in existing_payslips:
                    if existing.date_from and existing.date_from.month == month and existing.date_from.year == year:
                        raise ValidationError(_(
                            "Cannot generate payslip. A payslip already exists for %(employee)s for the month of %(month)02d/%(year)d."
                        ) % {
                            'employee': payslip.employee_id.name,
                            'month': month,
                            'year': year
                        })

    @api.onchange('employee_id', 'date_from')
    def _onchange_employee_month(self):
        if self.employee_id and self.date_from:
            month = self.date_from.month
            year = self.date_from.year
            
            domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '!=', 'cancel'),
            ]
            if self._origin and self._origin.id:
                domain.append(('id', '!=', self._origin.id))
                
            existing_payslips = self.env['hr.payslip'].search(domain)
            for existing in existing_payslips:
                if existing.date_from and existing.date_from.month == month and existing.date_from.year == year:
                    employee_name = self.employee_id.name
                    # Clear the selected employee
                    self.employee_id = False
                    
                    return {
                        'warning': {
                            'title': _("Duplicate Month Validation"),
                            'message': _("A payslip already exists for %(employee)s for the month of %(month)02d/%(year)d.\n\nThe employee has been deselected.") % {
                                'employee': employee_name,
                                'month': month,
                                'year': year
                            }
                        }
                    }

