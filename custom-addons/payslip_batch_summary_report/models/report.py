from odoo import api, models


class BatchSummaryReport(models.AbstractModel):
    _name = "report.payslip_batch_summary_report.batch_summary"
    _description = "Batch Summary Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Data is passed from the wizard
        if not data:
            data = {}

        # Fetch the batch using sudo to bypass security
        batch = self.env["hr.payslip.run"].sudo().browse(data.get("batch_id"))
        if not batch:
            batch = self.env["hr.payslip.run"].sudo().browse(docids)  # fallback

        payslips = batch.slip_ids.sorted("employee_id")
        currency = batch.company_id.currency_id

        # Compute per-payslip data
        payslip_data = []
        totals = {
            "monthly_rate": 0.0,
            "half_month": 0.0,
            "daily_rate": 0.0,
            "total_hours": 0.0,
            "hourly_rate": 0.0,
            "add": 0.0,
            "gross": 0.0,
            "undertime_hrs": 0.0,
            "undertime_amt": 0.0,
            "cash_advance": 0.0,
            "pagibig": 0.0,
            "philhealth": 0.0,
            "sss": 0.0,
            "total_deduction": 0.0,
            "netpay": 0.0,
        }

        for p in payslips:
            monthly = p.contract_id.wage or 0.0
            half = p.x_salary_half or 0.0
            daily = p.x_salary_daily or 0.0
            total_hrs = (
                (p.x_actual_regular_day or 0)
                + (p.x_actual_regular_holiday or 0)
                + (p.x_actual_specialnw_holiday or 0)
                + (p.x_actual_specialw_holiday or 0)
            )
            hourly = daily / 8 if daily else 0.0
            add_amt = p.x_add_amount_stored or 0.0
            gross = p.x_gross_total_stored or 0.0
            undertime_hrs = p.x_undertime_hrs or 0.0
            undertime_amt = p.x_undertime_amount or 0.0
            cash_adv = p.x_cash_advance_amount or 0.0
            pagibig = p.x_pagibig_amount_display if p.x_is_contribution_day else 0.0
            philhealth = (
                p.x_philhealth_amount_display if p.x_is_contribution_day else 0.0
            )
            sss = p.x_sss_amount_display if p.x_is_contribution_day else 0.0
            total_ded = p.x_deduction_total_stored or 0.0
            net = gross - total_ded

            line = {
                "employee_name": p.employee_id.name,
                "monthly_rate": monthly,
                "half_month": half,
                "daily_rate": daily,
                "total_hours": total_hrs,
                "hourly_rate": hourly,
                "add": add_amt,
                "gross": gross,
                "undertime_hrs": undertime_hrs,
                "undertime_amt": undertime_amt,
                "cash_advance": cash_adv,
                "pagibig": pagibig,
                "philhealth": philhealth,
                "sss": sss,
                "total_deduction": total_ded,
                "netpay": net,
            }
            payslip_data.append(line)
            # Accumulate totals
            for key in totals:
                totals[key] += line[key]

        # Meta-summary fields
        # x_working_days  = working days in the batch period (excl. holidays)
        # x_regular_day   = working days for the full month (excl. holidays)
        # x_overall_working_days = working days in the batch period (incl. holidays)
        work_days = batch.x_working_days or 0.0
        regular_day = batch.x_regular_day or 0.0
        overall_working_days = batch.x_overall_working_days or 0.0
        meta = {
            # Work Days = working days in the batch period excluding holidays
            "work_days": work_days,
            # Regular Days = working days in the full calendar month excluding holidays
            "regular_days": regular_day,
            # Hour/Month = full-month regular days × 8 hrs
            "hour_month": regular_day * 8,
            # Regular Hours = batch-period working days (excl. holidays) × 8 hrs
            "regular_hours": work_days * 8,
            # Util Days/Month = working days in the batch period INCLUDING holidays
            "util_days_month": overall_working_days,
            # Util Reg. Days = half of the full-month regular days (semi-monthly)
            "util_reg_days": regular_day / 2 if regular_day else 0.0,
        }

        # Company info
        company = batch.company_id

        # Return all data
        return {
            "doc_ids": payslips.ids,
            "doc_model": "hr.payslip",
            "data": data,
            "company": company,
            "batch": batch,
            "batch_name": batch.name or "",
            "batch_date_from": batch.date_start,
            "batch_date_to": batch.date_end,
            "payslip_data": payslip_data,
            "totals": totals,
            "meta": meta,
            "currency": currency,
            "preparer_name": data.get("preparer_name", ""),
            "preparer_title": data.get("preparer_title", ""),
            "approver_name": data.get("approver_name", ""),
            "approver_title": data.get("approver_title", ""),
        }
