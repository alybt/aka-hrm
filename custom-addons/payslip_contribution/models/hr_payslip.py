from odoo import api, fields, models

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # ------------------------------------------------------------
    # Override the total computation to respect x_is_contribution_day
    # ------------------------------------------------------------
    def _get_category_total(self, category_code, include_contributions=True):
        """
        Extended version: for DEDUCTION category, we can filter out contributions
        if x_is_contribution_day is False.
        """
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda line: line.category_id and line.category_id.code == category_code
        )

        # For DEDUCTION category, apply the contribution day filter
        if category_code == 'DEDUCTION' and not self.x_is_contribution_day:
            # Filter out lines that are contributions (by code pattern)
            contribution_codes = ['PHILHEALTH', 'SSS', 'PAGIBIG', 'HDMF']
            lines = lines.filtered(
                lambda line: not (line.code and line.code.upper() in contribution_codes)
            )

        return sum(lines.mapped("total"))

    @api.depends("line_ids", "line_ids.total", "line_ids.category_id", "x_is_contribution_day")
    def _compute_category_totals(self):
        for payslip in self:
            payslip.x_gross_total = payslip._get_category_total("GROSS")
            payslip.x_deduction_total = payslip._get_category_total("DEDUCTION")

    # ------------------------------------------------------------
    # Override the grouping method for the report
    # ------------------------------------------------------------
    def get_grouped_salary_lines_enhanced(self):
        """Same as before, but skip contribution lines when x_is_contribution_day is False."""
        self.ensure_one()
        result = {"GROSS": {}, "DEDUCTION": {}, "NETPAY": [], "SUMMARY": []}

        deduction_patterns = {
            "Undertime": ["UNDER", "UT"],
            "Contribution": ["PHILHEALTH", "SSS", "PAGIBIG", "HDMF"],
            "Loans": ["LOAN", "CA", "CASHADV", "SALOAN"],
            "Taxes": ["TAX", "WITHHOLDING", "WTAX"],
        }

        gross_patterns = {
            "Working Hours": ["BASIC", "REG", "REGHR", "REGHLDYHRS", "HLDYSNW", "HLDYSW"],
            "Allowances": ["ALLOW", "ALLOWANCE"],
            "Reimbursement": ["RMBRST", "REIMB", "REIMBURSE"],
            "Bonuses": ["BONUS", "13TH", "13THMONTH"],
        }

        for cat in deduction_patterns:
            result["DEDUCTION"][cat] = []
        result["DEDUCTION"]["Others"] = []
        for cat in gross_patterns:
            result["GROSS"][cat] = []
        result["GROSS"]["Others"] = []

        for line in self.line_ids.filtered(lambda l: l.appears_on_payslip and l.amount != 0):
            if not line.category_id:
                continue

            main_category = line.category_id.code.upper() if line.category_id.code else ""
            rule_code = line.code.upper() if line.code else ""

            # ---- Contribution day filter ----
            if (main_category == "DEDUCTION" and
                not self.x_is_contribution_day and
                any(code in rule_code for code in ["PHILHEALTH", "SSS", "PAGIBIG", "HDMF"])):
                continue  # skip this contribution line entirely

            if main_category == "GROSS":
                matched = False
                for sub_cat, codes in gross_patterns.items():
                    if rule_code in codes or any(code in rule_code for code in codes):
                        result["GROSS"][sub_cat].append(line)
                        matched = True
                        break
                if not matched:
                    result["GROSS"]["Others"].append(line)

            elif main_category == "DEDUCTION":
                matched = False
                for sub_cat, codes in deduction_patterns.items():
                    if rule_code in codes or any(code in rule_code for code in codes):
                        result["DEDUCTION"][sub_cat].append(line)
                        matched = True
                        break
                if not matched:
                    result["DEDUCTION"]["Others"].append(line)

            elif main_category == "NETPAY":
                result["NETPAY"].append(line)
            elif main_category == "SUMMARY":
                result["SUMMARY"].append(line)

        return result