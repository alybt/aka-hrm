from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_is_contribution_day = fields.Boolean(
        string="Contribution Day",
        help="Check if this payslip includes government contributions"
    )

    x_sss_amount_display = fields.Float(
        string="SSS Amount",
        compute='_compute_contribution_amounts',
        store=False,
        help="SSS amount from contract"
    )
    x_philhealth_amount_display = fields.Float(
        string="PhilHealth Amount",
        compute='_compute_contribution_amounts',
        store=False,
        help="PhilHealth amount from contract"
    )
    x_pagibig_amount_display = fields.Float(
        string="Pag-IBIG Amount",
        compute='_compute_contribution_amounts',
        store=False,
        help="Pag-IBIG amount from contract"
    )

    @api.depends('contract_id')
    def _compute_contribution_amounts(self):
        """Fetch contribution amounts from contract for display"""
        for payslip in self:
            if payslip.contract_id:
                payslip.x_sss_amount_display = payslip.contract_id.x_sss_contribution or 0.0
                payslip.x_philhealth_amount_display = payslip.contract_id.x_philhealth_contribution or 0.0
                payslip.x_pagibig_amount_display = payslip.contract_id.x_pagibig_contribution or 0.0
            else:
                payslip.x_sss_amount_display = 0.0
                payslip.x_philhealth_amount_display = 0.0
                payslip.x_pagibig_amount_display = 0.0

    @api.onchange('x_is_contribution_day')
    def _onchange_contribution_day(self):
        """When contribution day changes, update input lines"""
        if self and self.contract_id and self.id: 
            self._update_contribution_lines()

    def _update_contribution_lines(self):
        """Update the input lines with contributions"""
        existing_lines = self.input_line_ids.filtered(
            lambda l: l.code in ['SSS_CONT', 'PHILHEALTH_CONT', 'PAGIBIG_CONT']
        )
        existing_lines.unlink()

        if self.x_is_contribution_day and self.contract_id:
            InputLine = self.env['hr.payslip.input']

            vals_list = []

            if self.contract_id.x_employee_sss_number and self.x_sss_amount_display > 0:
                vals_list.append({
                    'payslip_id': self.id,
                    'name': 'SSS Contribution',
                    'code': 'SSS_CONT',
                    'amount': self.x_sss_amount_display,
                    'contract_id': self.contract_id.id,
                })

            if self.contract_id.x_employee_philhealth_number and self.x_philhealth_amount_display > 0:
                vals_list.append({
                    'payslip_id': self.id,
                    'name': 'PhilHealth Contribution',
                    'code': 'PHILHEALTH_CONT',
                    'amount': self.x_philhealth_amount_display,
                    'contract_id': self.contract_id.id,
                })

            if self.contract_id.x_employee_pagibig_number and self.x_pagibig_amount_display > 0:
                vals_list.append({
                    'payslip_id': self.id,
                    'name': 'Pag-IBIG Contribution',
                    'code': 'PAGIBIG_CONT',
                    'amount': self.x_pagibig_amount_display,
                    'contract_id': self.contract_id.id,
                })

            if vals_list:
                InputLine.create(vals_list)

    def compute_sheet(self):
        """Override compute_sheet to include contributions"""
        for payslip in self:
            if payslip.id:
                payslip._update_contribution_lines()

        return super().compute_sheet()

    @api.model
    def create(self, vals):
        """Override create to handle contribution lines after record creation"""
        payslip = super().create(vals)

        if payslip.x_is_contribution_day and payslip.contract_id:
            payslip._update_contribution_lines()

        return payslip

    def write(self, vals):
        """Override write to handle contribution lines when checkbox changes"""
        result = super().write(vals)

        if 'x_is_contribution_day' in vals:
            for payslip in self:
                if payslip.contract_id:
                    payslip._update_contribution_lines()

        return result