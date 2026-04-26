from odoo import models, fields, api
from datetime import datetime, timedelta, date
import calendar

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Removed x_regular_days as requested
    x_regular_holiday = fields.Float(string="Regular Holiday Count", compute="_compute_holiday_counts", store=True)
    x_specialw_holiday = fields.Float(string="Special Working Holiday", compute="_compute_holiday_counts", store=True)
    x_specialn_holiday = fields.Float(string="Special Non-Working Holiday", compute="_compute_holiday_counts", store=True)
    x_local_holiday = fields.Float(string="Local Holiday", compute="_compute_holiday_counts", store=True)

    @api.depends('date_from', 'employee_id')
    def _compute_holiday_counts(self):
        for rec in self:
            # Reset counters
            rec.x_regular_holiday = 0
            rec.x_specialw_holiday = 0
            rec.x_specialn_holiday = 0
            rec.x_local_holiday = 0

            if not rec.date_from or not rec.employee_id:
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            # Define the month boundaries
            year = rec.date_from.year
            month = rec.date_from.month
            _, last_day = calendar.monthrange(year, month)
            month_start = date(year, month, 1)
            month_end = date(year, month, last_day)

            # Search for holidays linked to the employee's calendar within this month
            holidays = self.env['resource.calendar.leaves'].search([
                ('calendar_id', '=', calendar_res.id),
                ('date_from', '<=', fields.Datetime.to_string(datetime.combine(month_end, datetime.max.time()))),
                ('date_to', '>=', fields.Datetime.to_string(datetime.combine(month_start, datetime.min.time()))),
            ])

            for h in holidays:
                # Calculate the duration within the current month bounds
                h_start = max(h.date_from.date(), month_start)
                h_end = min(h.date_to.date(), month_end)
                duration = (h_end - h_start).days + 1
                
                if duration <= 0:
                    continue

                # Sort by the Selection field defined in your resource.calendar.leaves inherit
                if h.x_holiday_types == 'regular':
                    rec.x_regular_holiday += duration
                elif h.x_holiday_types == 'special_non_working':
                    rec.x_specialn_holiday += duration
                elif h.x_holiday_types == 'special_working':
                    rec.x_specialw_holiday += duration
                elif h.x_holiday_types == 'local':
                    rec.x_local_holiday += duration