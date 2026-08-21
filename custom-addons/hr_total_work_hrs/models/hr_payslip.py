from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_total_work_hours = fields.Float(
        string="Total Actual Work Hours",
        compute="_compute_x_total_work_hours",
        store=True,
        help="Sum of all attendance logs within this payslip period."
    )

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_x_total_work_hours(self):
        for slip in self:
            if slip.employee_id and slip.date_from and slip.date_to:
                # Search for attendance records within the date range
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', slip.employee_id.id),
                    ('check_in', '>=', slip.date_from),
                    ('check_out', '<=', slip.date_to)
                ])

                # Sum the worked_hours field from hr.attendance
                total = sum(attendance.worked_hours for attendance in attendances)
                slip.x_total_work_hours = total
            else:
                slip.x_total_work_hours = 0.0