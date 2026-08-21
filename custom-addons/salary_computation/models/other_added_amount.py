from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    x_add_amount_stored = fields.Monetary(
        string="Added Amount (Stored)",
        compute="_compute_add_amount_stored",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("line_ids.total", "line_ids.category_id", "line_ids.code")
    def _compute_add_amount_stored(self):
        working_hours_codes = ["BASIC", "REG", "REGHR", "REGHLDYHRS", "HLDYSNW", "HLDYSW"]
        for payslip in self:
            if not payslip.line_ids:
                payslip.x_add_amount_stored = 0.0
                continue
            gross_lines = payslip.line_ids.filtered(
                lambda l: l.category_id
                and l.category_id.code == "GROSS"
                and l.code
                and l.code.upper() not in working_hours_codes
            )
            payslip.x_add_amount_stored = sum(gross_lines.mapped("total"))
