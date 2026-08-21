from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # Add missing currency field
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
        store=True,
    )

    x_gross_total = fields.Monetary(
        string="Gross Total",
        compute="_compute_category_totals",
        store=False,
        currency_field="currency_id",
    )

    x_deduction_total = fields.Monetary(
        string="Deduction Total",
        compute="_compute_category_totals",
        store=False,
        currency_field="currency_id",
    )

    def _get_category_total(self, category_code):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda line: line.category_id and line.category_id.code == category_code
        )
        return sum(lines.mapped("total"))

    @api.depends("line_ids", "line_ids.total", "line_ids.category_id")
    def _compute_category_totals(self):
        for payslip in self:
            payslip.x_gross_total = payslip._get_category_total("GROSS")
            payslip.x_deduction_total = payslip._get_category_total("DEDUCTION")
