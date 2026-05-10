from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    x_time_bank = fields.Float(
        string='Time Bank Balance',
        default=0.0
    )

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()

        for slip in self:
            total_ot = 0.0

            # Get overtime from each field if it exists
            if hasattr(slip, 'x_ot_regular_hours'):
                total_ot += slip.x_ot_regular_hours or 0.0
            if hasattr(slip, 'x_ot_regular_holiday_hours'):
                total_ot += slip.x_ot_regular_holiday_hours or 0.0
            if hasattr(slip, 'x_ot_specialnw_holiday_hours'):
                total_ot += slip.x_ot_specialnw_holiday_hours or 0.0
            if hasattr(slip, 'x_ot_specialw_holiday_hours'):
                total_ot += slip.x_ot_specialw_holiday_hours or 0.0

            if total_ot > 0 and slip.employee_id:
                slip.employee_id.x_time_bank = (slip.employee_id.x_time_bank or 0.0) + total_ot

        return res