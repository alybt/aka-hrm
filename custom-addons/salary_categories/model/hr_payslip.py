from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def get_grouped_salary_lines_enhanced(self):
        """
        Enhanced version with automatic categorization
        Hardcoded salary rules are organized into specific categories.
        Any new salary rules automatically go into 'Others'.
        """
        self.ensure_one()

        result = {"GROSS": {}, "DEDUCTION": {}, "NETPAY": [], "SUMMARY": []}

        # Define patterns for automatic categorization
        deduction_patterns = {
            "Undertime": ["UNDER", "UT"],
            "Contribution": ["PHILHEALTH", "SSS", "PAGIBIG", "HDMF"],
            "Loans": ["LOAN", "CA", "CASHADV", "SALOAN"],
            "Taxes": ["TAX", "WITHHOLDING", "WTAX"],
        }

        gross_patterns = {
            "Working Hours": [
                "BASIC",
                "REG",
                "REGHR",
                "REGHLDYHRS",
                "HLDYSNW",
                "HLDYSW",
            ],
            "Allowances": ["ALLOW", "ALLOWANCE"],
            "Reimbursement": ["RMBRST", "REIMB", "REIMBURSE"],
            "Bonuses": ["BONUS", "13TH", "13THMONTH"],
        }

        # Initialize sub-categories
        for cat in deduction_patterns:
            result["DEDUCTION"][cat] = []
        result["DEDUCTION"]["Others"] = []

        for cat in gross_patterns:
            result["GROSS"][cat] = []
        result["GROSS"]["Others"] = []

        for line in self.line_ids.filtered(
            lambda l: l.appears_on_payslip and l.amount != 0
        ):
            if not line.category_id:
                continue

            main_category = (
                line.category_id.code.upper() if line.category_id.code else ""
            )
            rule_code = line.code.upper() if line.code else ""

            if main_category == "GROSS":
                matched = False
                for sub_cat, codes in gross_patterns.items():
                    if rule_code in codes or any(code in rule_code for code in codes):
                        result["GROSS"][sub_cat].append(line)
                        matched = True
                        break
                if not matched:
                    # Any new GROSS rule goes to Others
                    result["GROSS"]["Others"].append(line)

            elif main_category == "DEDUCTION":
                matched = False
                for sub_cat, codes in deduction_patterns.items():
                    if rule_code in codes or any(code in rule_code for code in codes):
                        result["DEDUCTION"][sub_cat].append(line)
                        matched = True
                        break
                if not matched:
                    # Any new DEDUCTION rule goes to Others
                    result["DEDUCTION"]["Others"].append(line)

            elif main_category == "NETPAY":
                result["NETPAY"].append(line)
            elif main_category == "SUMMARY":
                result["SUMMARY"].append(line)

        return result

    # grouped_salary_lines_enhanced = fields.Serialized(
    #     compute="_compute_grouped_salary_lines"
    # )

    # def _compute_grouped_salary_lines(self):
    #     for rec in self:
    #         rec.grouped_salary_lines_enhanced = rec.get_grouped_salary_lines_enhanced()
