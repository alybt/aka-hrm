from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_working_days = fields.Float(
        string="Working Days",
        compute="_compute_working_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_working_days(self):
        for rec in self:
            rec.x_working_days = 0

            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            allowed_weekdays = set(int(att.dayofweek) for att in calendar_res.attendance_ids)

            work_days_count = 0
            current = rec.date_from

            while current <= rec.date_to:
                if current.weekday() in allowed_weekdays:
                    work_days_count += 1
                current += timedelta(days=1)

            start_dt = datetime.combine(rec.date_from, datetime.min.time())
            end_dt = datetime.combine(rec.date_to, datetime.max.time())

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(end_dt)),
                ('date_to', '>=', fields.Datetime.to_string(start_dt)),
            ])

            holiday_days = sum(1 for h in holidays if h.x_holiday_types)

            rec.x_working_days = work_days_count - holiday_days
        for rec in self:
            rec.x_working_days = 0

            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            work_days_count = 0
            current = rec.date_from

            allowed_weekdays = [int(att.dayofweek) for att in calendar_res.attendance_ids]

            while current <= rec.date_to:
                if current.weekday() in allowed_weekdays:
                    work_days_count += 1
                current += timedelta(days=1)

            start_dt = fields.Datetime.to_string(datetime.combine(rec.date_from, datetime.min.time()))
            end_dt = fields.Datetime.to_string(datetime.combine(rec.date_to, datetime.max.time()))

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', end_dt),
                ('date_to', '>=', start_dt),
            ])

            holiday_days = sum(1 for h in holidays if h.x_holiday_types)

            rec.x_working_days = work_days_count - holiday_days