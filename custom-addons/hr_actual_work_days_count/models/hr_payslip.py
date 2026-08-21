from odoo import models, fields, api
from datetime import timedelta, datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Field definitions
    x_actual_regular_day = fields.Float(string='Actual Regular Days', compute='_compute_actual_days_breakdown', store=True)
    x_actual_regular_holiday = fields.Float(string='Actual Regular Holiday', compute='_compute_actual_days_breakdown', store=True)
    x_actual_specialnw_holiday = fields.Float(string='Actual Special Non-Working', compute='_compute_actual_days_breakdown', store=True)
    x_actual_specialw_holiday = fields.Float(string='Actual Special Working', compute='_compute_actual_days_breakdown', store=True)
    x_actual_local_holiday = fields.Float(string='Actual Local Holiday', compute='_compute_actual_days_breakdown', store=True)

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_actual_days_breakdown(self):
        for rec in self:
            # Initialize all values to zero
            reg_h = snw_h = sw_h = loc_h = work_days_count = 0.0

            if not rec.date_from or not rec.date_to or not rec.employee_id:
                rec.update({
                    'x_actual_regular_day': 0, 'x_actual_regular_holiday': 0,
                    'x_actual_specialnw_holiday': 0, 'x_actual_specialw_holiday': 0,
                    'x_actual_local_holiday': 0
                })
                continue

            calendar_res = rec.employee_id.resource_calendar_id
            if not calendar_res:
                continue

            allowed_weekdays = set(int(att.dayofweek) for att in calendar_res.attendance_ids)

            current = rec.date_from
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
                ('resource_id', '=', False),
            ])

            for h in holidays:
                if h.x_holiday_types == 'regular':
                    reg_h += 1
                elif h.x_holiday_types == 'special_non_working':
                    snw_h += 1
                elif h.x_holiday_types == 'special_working':
                    sw_h += 1
                elif h.x_holiday_types == 'local':
                    loc_h += 1

            rec.x_actual_regular_holiday = reg_h
            rec.x_actual_specialnw_holiday = snw_h
            rec.x_actual_specialw_holiday = sw_h
            rec.x_actual_local_holiday = loc_h


            rec.x_actual_regular_day = work_days_count - (reg_h + snw_h + loc_h)

    @api.onchange('x_actual_regular_holiday', 'x_actual_specialnw_holiday')
    def _update_worked_days_from_holidays(self):
        """
        Automatically adds/updates lines in the Worked Days tab
        based on your custom 'Actual' day fields.
        """
        for payslip in self:
            # List of holidays to sync
            holidays = [
                ('REG_HOL', payslip.x_actual_regular_holiday),
                ('SPCL_NW', payslip.x_actual_specialnw_holiday),
                ('SPCL_W', payslip.x_actual_specialw_holiday),
            ]

            worked_days_lines = payslip.worked_days_line_ids
            for code, days in holidays:
                if days > 0:
                    # Look for existing line with this code
                    line = worked_days_lines.filtered(lambda l: l.code == code)
                    if line:
                        line.number_of_days = days
                        line.number_of_hours = days * 8
                    else:
                        # Create new line if it doesn't exist
                        create_vals = {
                            'name': code.replace('_', ' ').title(),
                            'code': code,
                            'number_of_days': days,
                            'number_of_hours': days * 8,
                            'contract_id': payslip.contract_id.id,
                        }
                        payslip.worked_days_line_ids = [(0, 0, create_vals)]
