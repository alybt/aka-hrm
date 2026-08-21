from odoo import api, fields, models


class PayslipBatchSummaryWizard(models.TransientModel):
    _name = "payslip.batch.summary.wizard"
    _description = "Wizard to set preparer/approver for batch summary"

    is_admin = fields.Boolean(compute="_compute_is_admin")

    preparer_id = fields.Many2one(
        "hr.employee",
        string="Prepared by",
        default=lambda self: self.env.user.employee_id,
        required=True,
    )
    approver_id = fields.Many2one(
        "hr.employee",
        string="Approved by",
        default=lambda self: self.env.user.employee_id,
        required=True,
    )
    batch_id = fields.Many2one(
        "hr.payslip.run",
        string="Payslip Batch",
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get("active_id"),
    )

    @api.depends_context("uid")
    def _compute_is_admin(self):
        for rec in self:
            rec.is_admin = (
                self.env.user.has_group("base.group_system") or
                self.env.is_admin() or
                self.env.user.has_group("hr.group_hr_manager") or
                self.env.user.has_group("hr.group_hr_user") or
                self.env.user.has_group("account.group_account_manager") or
                self.env.user.has_group("hr_payroll.group_hr_payroll_manager") or
                self.env.user.has_group("hr_payroll.group_hr_payroll_user")
            )

    def action_print_report(self):
        """Launch the report with wizard data."""
        return self.env.ref(
            "payslip_batch_summary_report.action_report_payslip_batch_summary"
        ).report_action(
            self,
            data={
                "wizard_id": self.id,
                "batch_id": self.batch_id.id,
                "preparer_name": self.preparer_id.name,
                "preparer_title": self.preparer_id.job_id.name or "",
                "approver_name": self.approver_id.name,
                "approver_title": self.approver_id.job_id.name or "",
            },
        )
