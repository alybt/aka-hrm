# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'  # <-- Targets the individual slip rows

    # ========== Contract Related Fields ==========
    contract_wage = fields.Float(
        string='Monthly Fixed Rate',
        compute='_compute_monthly_wage',
        store=True,
        readonly=True
    )

    salary_half = fields.Float(
        string='Half Salary',
        compute='_compute_salary_half',
        store=True,
        readonly=True
    )

    total_hours = fields.Float(
        string='Total Hours',
        compute='_compute_total_hours',
        store=True,
        readonly=True
    )

    hourly_rate = fields.Float(
        string='Hourly Rate',
        compute='_compute_hourly_rate',
        store=True,
        readonly=True
    )

    daily_rate = fields.Float(
        string='Daily Rate',
        compute='_compute_daily_rate',
        store=True,
        readonly=True
    )

    gross_pay = fields.Float(
        string='Gross Pay',
        compute='_compute_gross_pay',
        store=True,
        readonly=True
    )

    pagibig_amount = fields.Float(
        string='Pag-IBIG Amount',
        compute='_compute_contributions',
        store=True,
        readonly=True
    )

    sss_amount = fields.Float(
        string='SSS Amount',
        compute='_compute_contributions',
        store=True,
        readonly=True
    )

    philhealth_amount = fields.Float(
        string='PhilHealth Amount',
        compute='_compute_contributions',
        store=True,
        readonly=True
    )

    undertime_hrs = fields.Float(
        string='Undertime Hours',
        compute='_compute_undertime',
        store=True,
        readonly=True
    )

    undertime_cost = fields.Float(
        string='Undertime Cost',
        compute='_compute_undertime',
        store=True,
        readonly=True
    )

    deductions = fields.Float(
        string='Total Deductions',
        compute='_compute_deductions',
        store=True,
        readonly=True
    )

    # ========== Compute Methods ==========

    @api.depends('contract_id.wage')
    def _compute_monthly_wage(self):
        for payslip in self:
            payslip.contract_wage = payslip.contract_id.wage or 0.0

    @api.depends('contract_id.wage', 'x_salary_half')
    def _compute_salary_half(self):
        for payslip in self:
            payslip.salary_half = payslip.x_salary_half if payslip.contract_id else 0.0

    @api.depends('x_working_days', 'x_undertime_hrs')
    def _compute_total_hours(self):
        for payslip in self:
            working_days = payslip.x_working_days or 0.0
            undertime = payslip.x_undertime_hrs or 0.0
            total = (working_days * 8) - undertime
            payslip.total_hours = max(total, 0.0)

    @api.depends('x_salary_daily')
    def _compute_hourly_rate(self):
        for payslip in self:
            daily = payslip.x_salary_daily or 0.0
            payslip.hourly_rate = daily / 8

    @api.depends('x_salary_daily')
    def _compute_daily_rate(self):
        for payslip in self:
            payslip.daily_rate = payslip.x_salary_daily or 0.0

    @api.depends('line_ids.total', 'line_ids.category_id.code')
    def _compute_gross_pay(self):
        for payslip in self:
            total_gross = 0.0
            for line in payslip.line_ids:
                if line.category_id and line.category_id.code == 'GROSS':
                    total_gross += line.total
            payslip.gross_pay = total_gross

    @api.depends('contract_id.x_sss_contribution', 'contract_id.x_philhealth_contribution', 'contract_id.x_pagibig_contribution')
    def _compute_contributions(self):
        for payslip in self:
            if payslip.contract_id:
                payslip.sss_amount = payslip.contract_id.x_sss_contribution or 0.0
                payslip.philhealth_amount = payslip.contract_id.x_philhealth_contribution or 0.0
                payslip.pagibig_amount = payslip.contract_id.x_pagibig_contribution or 0.0
            else:
                payslip.sss_amount = payslip.philhealth_amount = payslip.pagibig_amount = 0.0

    @api.depends('x_undertime_hrs', 'x_salary_daily')
    def _compute_undertime(self):
        for payslip in self:
            undertime_hours = payslip.x_undertime_hrs or 0.0
            daily_rate = payslip.x_salary_daily or 0.0
            payslip.undertime_hrs = undertime_hours
            if undertime_hours > 0 and daily_rate > 0:
                payslip.undertime_cost = undertime_hours * (daily_rate / 8)
            else:
                payslip.undertime_cost = 0.0

    @api.depends('line_ids.total', 'line_ids.code')
    def _compute_deductions(self):
        deduction_codes = ['SSS', 'PHILHEALTH', 'PAGIBIG', 'TAX']
        for payslip in self:
            total_deductions = 0.0
            for line in payslip.line_ids:
                if line.code in deduction_codes:
                    total_deductions += line.total
            payslip.deductions = total_deductions