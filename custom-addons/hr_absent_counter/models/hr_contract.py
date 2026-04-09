from odoo import api, fields, models

class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    deduct_absences = fields.Boolean(
        string='Deduct Absences from Salary',
        default=True,
        help="If checked, absences will be automatically deducted from salary"
    )
    working_days_per_month = fields.Integer(
        string='Working Days per Month',
        default=26,
        help="Number of working days per month for daily rate calculation"
    )
    
    def get_daily_rate(self):
        """Calculate daily rate based on monthly wage"""
        self.ensure_one()
        if self.wage and self.working_days_per_month:
            return self.wage / self.working_days_per_month
        return 0.0