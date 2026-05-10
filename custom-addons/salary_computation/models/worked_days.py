from odoo import models, fields, api
from datetime import datetime, time


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_worked_regular_hours = fields.Float(
        string="Regular Hours",
        compute="_compute_work_hours_breakdown",
        store=True
    )
    x_worked_regular_holiday_hours = fields.Float(
        string="Regular Holiday Hours",
        compute="_compute_work_hours_breakdown",
        store=True
    )
    x_worked_specialnw_holiday_hours = fields.Float(
        string="Special NW Holiday Hours",
        compute="_compute_work_hours_breakdown",
        store=True
    )
    x_worked_specialw_holiday_hours = fields.Float(
        string="Special Working Holiday Hours",
        compute="_compute_work_hours_breakdown",
        store=True
    )

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_work_hours_breakdown(self):
        for slip in self:
            regular_hours = 0.0
            regular_holiday_hours = 0.0
            special_nw_hours = 0.0
            special_w_hours = 0.0

            if slip.employee_id and slip.date_from and slip.date_to:
                # 1. Get all holidays/leaves for the employee's calendar within the payslip period
                holiday_leaves = self.env['resource.calendar.leaves'].search([
                    ('calendar_id', '=', slip.employee_id.resource_calendar_id.id),
                    ('date_from', '<=', fields.Datetime.to_string(datetime.combine(slip.date_to, time.max))),
                    ('date_to', '>=', fields.Datetime.to_string(datetime.combine(slip.date_from, time.min)))
                ])

                # Create a map of date -> holiday type
                holiday_map = {}
                for leaf in holiday_leaves:
                    current_date = leaf.date_from.date()
                    while current_date <= leaf.date_to.date():
                        holiday_map[current_date] = leaf.x_holiday_types
                        current_date = fields.Date.add(current_date, days=1)

                # 2. Search for attendance records within the date range
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', slip.employee_id.id),
                    ('check_in', '>=', slip.date_from),
                    ('check_out', '<=', slip.date_to)
                ])

                # 3. Categorize hours based on the date's holiday type
                for attendance in attendances:
                    attendance_date = attendance.check_in.date() if attendance.check_in else None
                    if attendance_date:
                        holiday_type = holiday_map.get(attendance_date, False)
                        worked_hours = attendance.worked_hours

                        if holiday_type == 'regular':
                            regular_holiday_hours += worked_hours
                        elif holiday_type == 'special_non_working':
                            special_nw_hours += worked_hours
                        elif holiday_type == 'special_working':
                            special_w_hours += worked_hours
                        else:
                            # No holiday - treat as regular hours
                            regular_hours += worked_hours

            # Assign values
            slip.update({
                'x_worked_regular_hours': regular_hours,
                'x_worked_regular_holiday_hours': regular_holiday_hours,
                'x_worked_specialnw_holiday_hours': special_nw_hours,
                'x_worked_specialw_holiday_hours': special_w_hours,
            })