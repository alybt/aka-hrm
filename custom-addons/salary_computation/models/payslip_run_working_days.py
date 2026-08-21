from odoo import models, fields, api
from datetime import timedelta, datetime, date
import calendar


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    x_working_days = fields.Float(
        string="Working Days (Excluding Holidays)",
        compute="_compute_batch_working_days",
        store=True
    )

    x_overall_working_days = fields.Float(
        string="Working Days (Including Holidays)",
        compute="_compute_batch_working_days",
        store=True
    )

    x_regular_day = fields.Float(
        string="Regular Days",
        compute="_compute_batch_regular_days",
        store=True
    )

    @api.depends('date_start', 'date_end')
    def _compute_batch_working_days(self):
        for rec in self:
            rec.x_working_days = 0
            rec.x_overall_working_days = 0

            if not rec.date_start or not rec.date_end:
                continue

            calendar_res = rec.company_id.resource_calendar_id or self.env.company.resource_calendar_id
            if not calendar_res:
                continue

            allowed_weekdays = set(int(att.dayofweek) for att in calendar_res.attendance_ids)

            work_days_count = 0
            current = rec.date_start

            while current <= rec.date_end:
                if current.weekday() in allowed_weekdays:
                    work_days_count += 1
                current += timedelta(days=1)

            start_dt = datetime.combine(rec.date_start, datetime.min.time())
            end_dt = datetime.combine(rec.date_end, datetime.max.time())

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(end_dt)),
                ('date_to', '>=', fields.Datetime.to_string(start_dt)),
            ])

            holiday_days = sum(1 for h in holidays if h.x_holiday_types)

            rec.x_working_days = work_days_count - holiday_days
            rec.x_overall_working_days = work_days_count

    @api.depends('date_start')
    def _compute_batch_regular_days(self):
        for rec in self:
            rec.x_regular_day = 0
            if not rec.date_start:
                continue

            calendar_res = rec.company_id.resource_calendar_id or self.env.company.resource_calendar_id
            if not calendar_res:
                continue

            year = rec.date_start.year
            month = rec.date_start.month

            _, last_day = calendar.monthrange(year, month)

            month_start = date(year, month, 1)
            month_end = date(year, month, last_day)

            work_days = 0
            current = month_start
            allowed_weekdays = [int(att.dayofweek) for att in calendar_res.attendance_ids]

            while current <= month_end:
                if current.weekday() in allowed_weekdays:
                    work_days += 1
                current += timedelta(days=1)

            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(datetime.combine(month_end, datetime.max.time()))),
                ('date_to', '>=', fields.Datetime.to_string(datetime.combine(month_start, datetime.min.time()))),
            ])

            holiday_days = sum(1 for h in holidays if h.x_holiday_types)
            rec.x_regular_day = work_days - holiday_days
