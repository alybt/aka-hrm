from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_regular_days = fields.Float(
        string="Regular Days",
        compute="_compute_regular_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_regular_days(self):
        for rec in self:
            rec.x_regular_days = 0

            if not rec.date_from or not rec.date_to or not rec.employee_id:
                continue

            # ❗ enforce same month
            if rec.date_from.month != rec.date_to.month:
                raise ValidationError("Payslip must be within one month only.")

            calendar = rec.employee_id.resource_calendar_id
            if not calendar:
                continue

            # count working days
            work_days = 0
            current = rec.date_from

            while current <= rec.date_to:
                weekday = str(current.weekday())
                if any(att.dayofweek == weekday for att in calendar.attendance_ids):
                    work_days += 1
                current += timedelta(days=1)

            # get holidays
            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar.id),
                ('date_from', '<=', rec.date_to),
                ('date_to', '>=', rec.date_from),
            ])

            holiday_days = sum(1 for h in holidays if h.x_holiday_types)

            rec.x_regular_days = work_days - holiday_days