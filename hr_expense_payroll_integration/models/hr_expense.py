# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    include_in_payroll = fields.Boolean(
        string="Include in Payroll",
        help="If checked, this expense will be reimbursed through payroll instead of direct payment",
        copy=False,
        tracking=True,
    )

    payroll_paid = fields.Boolean(
        string="Paid via Payroll",
        help="True if the expense has been paid through payroll",
        copy=False,
        readonly=True,
        tracking=True,
    )

    payroll_paid_date = fields.Date(
        string="Payroll Payment Date",
        readonly=True,
        help="Date when the expense was paid through payroll",
    )

    @api.constrains('include_in_payroll', 'payment_mode')
    def _check_payroll_payment_mode(self):
        for expense in self:
            if expense.include_in_payroll and expense.payment_mode == 'company_account':
                raise UserError(_("Only expenses paid by employee (own_account) can be included in payroll."))

    @api.onchange('payment_mode')
    def _onchange_payment_mode_payroll(self):
        """Clear payroll option if payment mode changes to company_account"""
        if self.payment_mode == 'company_account' and self.include_in_payroll:
            self.include_in_payroll = False
            return {
                'warning': {
                    'title': _('Payroll Option Cleared'),
                    'message': _('Company account expenses cannot be included in payroll. The payroll option has been unchecked.')
                }
            }

    def action_submit_expenses(self):
        """Override to set payroll option on expense sheet based on expenses"""
        # Call parent method first
        result = super().action_submit_expenses()
        
        # If expenses are being submitted, set payroll option on the sheet
        if self and any(expense.include_in_payroll for expense in self):
            # Get the created expense sheets from the result
            if result.get('res_id'):
                sheet = self.env['hr.expense.sheet'].browse(result['res_id'])
                if sheet:
                    sheet.include_in_payroll = any(expense.include_in_payroll for expense in self)
        
        return result

    def action_mark_payroll_paid(self):
        """Mark individual expense as paid through payroll"""
        if not self.include_in_payroll:
            raise UserError(_("Only expenses marked for payroll can be marked as paid via payroll."))
        
        if self.state not in ['approved']:
            raise UserError(_("Only approved expenses can be marked as paid via payroll."))
        
        self.write({
            'payroll_paid': True,
            'payroll_paid_date': fields.Date.context_today(self),
        })

        # Update the sheet if all expenses are paid
        if self.sheet_id:
            sheet_expenses = self.sheet_id.expense_line_ids.filtered(lambda exp: exp.include_in_payroll)
            if all(exp.payroll_paid for exp in sheet_expenses):
                self.sheet_id.action_mark_payroll_paid()
