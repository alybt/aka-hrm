from odoo import models, fields, api
from datetime import timedelta

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_absent_days = fields.Float(
        string="Absent Days",
        compute="_compute_absent_days",
        store=True
    )

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_absent_days(self):
        for slip in self:
            absent_days = 0

            if not slip.date_from or not slip.date_to or not slip.employee_id:
                slip.x_absent_days = 0
                continue

            # Get contract
            contract = slip.contract_id
            if not contract or not contract.resource_calendar_id:
                slip.x_absent_days = 0
                continue

            calendar = contract.resource_calendar_id

            current_date = slip.date_from

            while current_date <= slip.date_to:

                # Check if it's a working day
                weekday = str(current_date.weekday())  # 0 = Monday

                working = any(
                    att.dayofweek == weekday
                    for att in calendar.attendance_ids
                )

                if working:
                    # Check if there is a work entry
                    work_entries = self.env['hr.work.entry'].search([
                        ('employee_id', '=', slip.employee_id.id),
                        ('date_start', '<=', current_date),
                        ('date_stop', '>=', current_date),
                    ])

                    # Check if attendance exists
                    has_attendance = any(
                        we.work_entry_type_id.code == 'WORK100'
                        for we in work_entries
                    )

                    if not has_attendance:
                        absent_days += 1

                current_date += timedelta(days=1)

            slip.x_absent_days = absent_days