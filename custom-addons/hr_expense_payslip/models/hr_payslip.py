from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    include_reimbursements = fields.Boolean(string="Include Reimbursements", default=True)

    # We remove store=True if you want it to be purely dynamic,
    # or keep it and add an onchange for the UI.
    x_reimbursement_total = fields.Float(
        string="Reimbursement Total",
        compute="_compute_reimbursement_total",
        store=True
    )

    expense_ids = fields.One2many('hr.expense', 'payslip_id', string="Reimbursements")

    @api.depends('expense_ids.total_amount', 'include_reimbursements')
    def _compute_reimbursement_total(self):
        for slip in self:
            if slip.include_reimbursements:
                slip.x_reimbursement_total = sum(slip.expense_ids.mapped('total_amount'))
            else:
                slip.x_reimbursement_total = 0.0

    @api.onchange('include_reimbursements')
    def _onchange_include_reimbursements(self):
        """
        Triggers immediately when the checkbox is clicked in the UI
        before the record is even saved.
        """
        if self.include_reimbursements:
            # Find candidate expenses to show the user what WILL be included
            unlinked_expenses = self.env['hr.expense'].search([
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'post'),
                ('is_reimbursed', '=', False),
                ('payslip_id', '=', False)
            ])
            # Temporary link for the UI preview
            self.expense_ids = unlinked_expenses
        else:
            # Clear the preview if unchecked
            self.expense_ids = [(5, 0, 0)]

        # Manually trigger the compute logic for the total
        self._compute_reimbursement_total()