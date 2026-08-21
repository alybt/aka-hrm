from odoo import models, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _compute_worked_days_line_ids(self):
        """
        Overwrite/Extend worked days to subtract Holiday hours from WORK100.
        """
        res = super(HrPayslip, self)._compute_worked_days_line_ids()

        for slip in self:
            # 1. Identify the lines
            work100_line = slip.worked_days_line_ids.filtered(lambda l: l.code == 'WORK100')
            # Adjust 'GLOBAL' to match your holiday work entry code (often GLOBAL or LEAVE110)
            holiday_line = slip.worked_days_line_ids.filtered(lambda l: l.code in ['GLOBAL', 'HOLIDAY'])

            if work100_line and holiday_line:
                # 2. Calculate the total holiday impact
                total_holiday_hours = sum(holiday_line.mapped('number_of_hours'))
                total_holiday_days = sum(holiday_line.mapped('number_of_days'))

                # 3. Subtract from WORK100
                # We use max(0, ...) to ensure we never have negative working hours
                work100_line.number_of_hours = max(0, work100_line.number_of_hours - total_holiday_hours)
                work100_line.number_of_days = max(0, work100_line.number_of_days - total_holiday_days)

        return res