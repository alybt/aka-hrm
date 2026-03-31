# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

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

    @api.depends('account_move_ids', 'payment_state', 'approval_state', 'payroll_paid')
    def _compute_state(self):
        for sheet in self:
            if sheet.payroll_paid:
                sheet.state = 'done'
            elif sheet.payment_state != 'not_paid':
                sheet.state = 'done'
            elif sheet.account_move_ids:
                sheet.state = 'post'
            elif sheet.approval_state:
                sheet.state = sheet.approval_state
            else:
                sheet.state = 'draft'

    def action_submit_sheet(self):
        # Check if payroll option is selected for company account expenses
        for sheet in self:
            if sheet.include_in_payroll and sheet.payment_mode == 'company_account':
                raise UserError(_("You cannot include company account expenses in payroll. Only employee-paid expenses can be reimbursed through payroll."))
        return super().action_submit_sheet()

    def action_sheet_move_create(self):
        # Skip creating accounting entries for payroll-included expenses
        payroll_sheets = self.filtered(lambda s: s.include_in_payroll)
        regular_sheets = self - payroll_sheets
        
        if regular_sheets:
            regular_sheets._check_can_create_move()
            regular_sheets._do_create_moves()
        
        # Mark payroll sheets as ready for payroll processing
        payroll_sheets.write({'state': 'approve'})

    def action_mark_payroll_paid(self):
        """Mark expense as paid through payroll"""
        if not self.include_in_payroll:
            raise UserError(_("Only expenses marked for payroll can be marked as paid via payroll."))
        
        if self.state != 'approve':
            raise UserError(_("Only approved expenses can be marked as paid via payroll."))
        
        self.write({
            'payroll_paid': True,
            'payroll_paid_date': fields.Date.context_today(self),
            'state': 'done'
        })

    def action_register_payment(self):
        """Override to prevent payment registration for payroll expenses"""
        if self.include_in_payroll and not self.payroll_paid:
            raise UserError(_("This expense is configured to be paid through payroll. Use 'Mark as Paid via Payroll' instead."))
        return super().action_register_payment()

    @api.constrains('include_in_payroll', 'payment_mode')
    def _check_payroll_payment_mode(self):
        for sheet in self:
            if sheet.include_in_payroll and sheet.payment_mode == 'company_account':
                raise UserError(_("Only expenses paid by employee (own_account) can be included in payroll."))
