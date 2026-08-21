from odoo import api, fields, models

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # Currency field (may already exist)
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
        store=True,
    )

    # Stored gross total (always includes all GROSS lines)
    x_gross_total_stored = fields.Monetary(
        string="Gross Total",
        compute="_compute_stored_totals",
        store=True,
        currency_field="currency_id",
    )

    # Stored deduction total (respects x_is_contribution_day)
    x_deduction_total_stored = fields.Monetary(
        string="Deduction Total",
        compute="_compute_stored_totals",
        store=True,
        currency_field="currency_id",
    )
    x_netpay_stored = fields.Monetary(
        string="Net Pay",
        compute="_compute_stored_totals",
        store=True,
        currency_field="currency_id",
    )

    # Helper to get total for a category, with optional contribution filter
    def _get_category_total(self, category_code, skip_contributions_if_false=False):
        """
        If skip_contributions_if_false is True and self.x_is_contribution_day is False,
        then any line whose code matches contribution patterns is excluded.
        """
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda l: l.category_id and l.category_id.code == category_code
        )

        if skip_contributions_if_false and not self.x_is_contribution_day:
            contribution_codes = ['PHILHEALTH', 'SSS', 'PAGIBIG', 'HDMF']
            lines = lines.filtered(
                lambda l: not (l.code and l.code.upper() in contribution_codes)
            )

        return sum(lines.mapped("total"))

    @api.depends("line_ids", "line_ids.total", "line_ids.category_id", "x_is_contribution_day")
    def _compute_stored_totals(self):
        for payslip in self:
            payslip.x_gross_total_stored = payslip._get_category_total("GROSS", skip_contributions_if_false=False)
            payslip.x_deduction_total_stored = payslip._get_category_total("DEDUCTION", skip_contributions_if_false=True)
            payslip.x_netpay_stored = payslip.x_gross_total_stored - payslip.x_deduction_total_stored