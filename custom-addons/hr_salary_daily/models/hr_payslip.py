from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_salary_daily = fields.Float(
        string="Daily Rate",
        compute="_compute_daily_salary",
        store=True
    )

    @api.depends('contract_id.wage')
    def _compute_daily_salary(self):
        for rec in self:
            if rec.contract_id and rec.contract_id.wage:
                rec.x_salary_daily = rec.contract_id.wage / rec.x_regular_days
            else:
                rec.x_salary_daily = 0