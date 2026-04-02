from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta, date
import calendar

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_regular_days = fields.Float(
        string="Regular Days",
        compute="_compute_regular_days",
        store=True
    )

    @api.depends('date_from', 'employee_id')
    def _compute_regular_days(self):
        for rec in self:
            rec.x_regular_days = 0
            if not rec.date_from or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            year = rec.date_from.year
            month = rec.date_from.month
            
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

            rec.x_regular_days = work_days - holiday_days