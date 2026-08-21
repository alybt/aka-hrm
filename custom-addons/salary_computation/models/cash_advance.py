from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    x_cash_advance_amount = fields.Monetary(
        string="Cash Advance Amount",
        compute="_compute_cash_advance_amount",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("line_ids.total", "line_ids.category_id", "line_ids.code", "line_ids.name")
    def _compute_cash_advance_amount(self):
        loan_codes = ["LOAN", "CA", "CASHADV", "SALOAN"]
        for payslip in self:
            if not payslip.line_ids:
                payslip.x_cash_advance_amount = 0.0
                continue
            loan_lines = payslip.line_ids.filtered(
                lambda l: l.category_id
                and l.category_id.code == "DEDUCTION"
                and (
                    (l.code and l.code.upper() in loan_codes)
                    or (l.name and "cash advance" in l.name.lower())
                )
            )
            payslip.x_cash_advance_amount = sum(loan_lines.mapped("total"))
