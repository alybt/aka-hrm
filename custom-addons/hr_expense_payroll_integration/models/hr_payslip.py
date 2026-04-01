# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    expense_reimbursement_ids = fields.One2many(
        'hr.expense.sheet', 
        compute='_compute_expense_reimbursements',
        string='Expense Reimbursements'
    )
    
    total_expense_reimbursement = fields.Monetary(
        compute='_compute_expense_reimbursements',
        string='Total Expense Reimbursement',
        currency_field='currency_id'
    )

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_expense_reimbursements(self):
        for payslip in self:
            expenses = self.env['hr.expense.sheet'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('include_in_payroll', '=', True),
                ('payroll_paid', '=', False),
                ('state', '=', 'approve'),
                ('accounting_date', '>=', payslip.date_from),
                ('accounting_date', '<=', payslip.date_to),
            ])
            payslip.expense_reimbursement_ids = expenses
            payslip.total_expense_reimbursement = sum(expenses.mapped('total_amount'))

    def compute_sheet(self):
        # Call parent computation first
        result = super().compute_sheet()
        
        # Add expense reimbursement lines
        for payslip in self:
            payslip._add_expense_reimbursement_lines()
        
        return result

    def _add_expense_reimbursement_lines(self):
        """Add expense reimbursement lines to the payslip"""
        expense_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'EXP_REIMB')
        ], limit=1)
        
        if not expense_rule:
            return
        
        for payslip in self:
            if payslip.total_expense_reimbursement > 0:
                # Remove existing expense reimbursement lines
                existing_lines = payslip.line_ids.filtered(lambda line: line.salary_rule_id.code == 'EXP_REIMB')
                if existing_lines:
                    existing_lines.unlink()
                
                # Add new expense reimbursement line
                payslip.line_ids.create({
                    'slip_id': payslip.id,
                    'salary_rule_id': expense_rule.id,
                    'employee_id': payslip.employee_id.id,
                    'contract_id': payslip.contract_id.id,
                    'rate': 100,
                    'amount': payslip.total_expense_reimbursement,
                    'total': payslip.total_expense_reimbursement,
                    'category_id': expense_rule.category_id.id,
                })

    def action_payslip_done(self):
        """Mark expense reimbursements as paid when payslip is confirmed"""
        result = super().action_payslip_done()
        
        for payslip in self:
            if payslip.expense_reimbursement_ids:
                payslip.expense_reimbursement_ids.action_mark_payroll_paid()
        
        return result

    def action_payslip_cancel(self):
        """Unmark expense reimbursements if payslip is cancelled"""
        result = super().action_payslip_cancel()
        
        for payslip in self:
            if payslip.expense_reimbursement_ids:
                payslip.expense_reimbursement_ids.write({
                    'payroll_paid': False,
                    'payroll_paid_date': False,
                    'state': 'approve'
                })
        
        return result
