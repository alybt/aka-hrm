from odoo import models, _
from odoo.exceptions import UserError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_print_summary_report(self):
        """Print the summary report for all payslips in this batch."""
        self.ensure_one()
        payslips = self.slip_ids
        if not payslips:
            raise UserError(_("No payslips found in this batch."))
        return self.env.ref('payslip_summary_report.action_payslip_summary_report').report_action(payslips)