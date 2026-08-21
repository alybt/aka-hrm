from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    payslip_id = fields.Many2one(
        'hr.payslip',
        string="Payslip",
        readonly=True,
        copy=False # Important: Don't copy the link if the expense is duplicated
    )

    is_reimbursed = fields.Boolean(
        string="Reimbursed in Payslip",
        default=False,
        copy=False,
        help="Technical field to prevent an expense from being paid twice."
    )

    def action_unpost_from_payslip(self):
        """ Helper method to release expenses if a payslip is cancelled """
        self.write({'is_reimbursed': False, 'payslip_id': False})