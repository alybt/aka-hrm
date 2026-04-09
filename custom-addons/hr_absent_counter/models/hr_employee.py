from odoo import api, fields, models

class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    last_absence_count = fields.Float(string='Last Absence Count', compute='_compute_last_absence_count')
    total_absences_year = fields.Float(string='Total Absences This Year', compute='_compute_total_absences_year')
    total_holidays_year = fields.Float(string='Total Holidays This Year', compute='_compute_total_absences_year')
    
    @api.depends('id')
    def _compute_last_absence_count(self):
        for employee in self:
            last_report = self.env['hr.absence.report'].search([
                ('employee_id', '=', employee.id)
            ], limit=1, order='create_date desc')
            
            employee.last_absence_count = last_report.absence_days if last_report else 0.0
    
    @api.depends('id')
    def _compute_total_absences_year(self):
        for employee in self:
            current_year = fields.Date.today().year
            year_reports = self.env['hr.absence.report'].search([
                ('employee_id', '=', employee.id),
                ('date_from', '>=', f'{current_year}-01-01'),
                ('date_to', '<=', f'{current_year}-12-31')
            ])
            
            employee.total_absences_year = sum(year_reports.mapped('absence_days'))
            employee.total_holidays_year = sum(year_reports.mapped('holiday_days'))
    
    def action_count_absences(self):
        """Open absence counting wizard"""
        return {
            'name': 'Count Absences (Excluding Holidays)',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.absence.count',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_date_from': fields.Date.today().replace(day=1),
                'default_date_to': fields.Date.today(),
            }
        }
    
    def action_view_absence_reports(self):
        """View absence reports for employee"""
        return {
            'name': 'Absence Reports',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.absence.report',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'target': 'current',
        }