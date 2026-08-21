from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # New OT Fields
    x_ot_regular_hours = fields.Float(string="OT Regular", compute="_compute_ot_hours", store=True)
    x_ot_regular_holiday_hours = fields.Float(string="OT Regular Holiday", compute="_compute_ot_hours", store=True)
    x_ot_specialnw_holiday_hours = fields.Float(string="OT Special NW Holiday", compute="_compute_ot_hours", store=True)
    x_ot_specialw_holiday_hours = fields.Float(string="OT Special W Holiday", compute="_compute_ot_hours", store=True)

    @api.depends(
        'x_actual_regular_day', 'x_worked_regular_hours',
        'x_actual_regular_holiday', 'x_worked_regular_holiday_hours',
        'x_actual_specialnw_holiday', 'x_worked_specialnw_holiday_hours',
        'x_actual_specialw_holiday', 'x_worked_specialw_holiday_hours'
    )
    def _compute_ot_hours(self):
        for slip in self:
            # Logic: If (Worked > Actual * 8), calculate the difference, else 0
            slip.x_ot_regular_hours = max(0, (slip.x_worked_regular_hours or 0.0) - ((slip.x_actual_regular_day or 0.0) * 8))

            slip.x_ot_regular_holiday_hours = max(0, (slip.x_worked_regular_holiday_hours or 0.0) - ((slip.x_actual_regular_holiday or 0.0) * 8))

            slip.x_ot_specialnw_holiday_hours = max(0, (slip.x_worked_specialnw_holiday_hours or 0.0) - ((slip.x_actual_specialnw_holiday or 0.0) * 8))

            slip.x_ot_specialw_holiday_hours = max(0, (slip.x_worked_specialw_holiday_hours or 0.0) - ((slip.x_actual_specialw_holiday or 0.0) * 8))