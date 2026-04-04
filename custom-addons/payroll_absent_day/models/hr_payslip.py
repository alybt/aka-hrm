from odoo import models, fields, api
from datetime import datetime, timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_absent_days = fields.Float(string="Absent Days", compute="_compute_attendance_metrics", store=True)
    x_undertime = fields.Float(string="Undertime (Hours)", compute="_compute_attendance_metrics", store=True)
    x_undertime_overall = fields.Float(string="Overall Undertime", compute="_compute_attendance_metrics", store=True)

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_attendance_metrics(self):
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue

            absent_count = 0
            total_undertime_minutes = 0
            calendar = slip.employee_id.resource_calendar_id
            
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('check_in', '>=', slip.date_from),
                ('check_out', '<=', slip.date_to)
            ])

            for att in attendances:
                check_in_local = att.check_in + timedelta(hours=8)
                check_out_local = att.check_out + timedelta(hours=8)

                work_start = check_in_local.replace(hour=8, minute=0, second=0)
                if check_in_local > work_start:
                    late_diff = (check_in_local - work_start).total_seconds() / 60
                    total_undertime_minutes += late_diff

                work_end = check_out_local.replace(hour=17, minute=0, second=0)
                if check_out_local < work_end:
                    early_diff = (work_end - check_out_local).total_seconds() / 60
                    total_undertime_minutes += early_diff

            expected_days = slip.x_working_days # Using your existing field
            days_worked = len(set(att.check_in.date() for att in attendances))
            absent_count = max(0, expected_days - days_worked)

            slip.x_absent_days = absent_count
            slip.x_undertime = total_undertime_minutes / 60 
            slip.x_undertime_overall = (absent_count * 8) + slip.x_undertime