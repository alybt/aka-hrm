from odoo import models, _
from odoo.exceptions import UserError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_print_batch_payslips(self):
        """
        Print all payslips in this batch using the custom payslip report.
        """
        self.ensure_one()
        payslips = self.slip_ids
        if not payslips:
            raise UserError(_("No payslips found in this batch."))
        report_action = self.env.ref('payslip_batch_payslip_print.action_report_batch_payslip')
        return report_action.report_action(payslips)