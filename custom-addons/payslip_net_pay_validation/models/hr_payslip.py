from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    # Net pay computed as Gross - Deductions
    x_net_pay = fields.Monetary(
        string="Net Pay",
        compute="_compute_net_pay",
        store=False,
        currency_field="currency_id",
    )

    @api.depends('x_gross_total', 'x_deduction_total')
    def _compute_net_pay(self):
        for payslip in self:
            gross = payslip.x_gross_total or 0.0
            deduction = payslip.x_deduction_total or 0.0
            payslip.x_net_pay = gross - deduction

    # Constraint: prevent confirming (validating) a payslip with negative net pay
    @api.constrains('state', 'x_net_pay')
    def _check_negative_net_pay(self):
        for payslip in self:
            if payslip.state == 'done' and payslip.x_net_pay < 0:
                raise ValidationError(_(
                    "Payslip %s has a negative net pay (%.2f). You cannot confirm a payslip with negative net pay.",
                    payslip.number,
                    payslip.x_net_pay
                ))

    def compute_sheet(self):
        if self.env.context.get('ignore_negative_net_pay'):
            return super().compute_sheet()
            
        self.env.cr.execute('SAVEPOINT check_negative_net_pay')
        res = super().compute_sheet()
        
        # Check net pay
        negative_slips = self.filtered(lambda p: p.x_net_pay < 0)
        
        if negative_slips:
            self.env.cr.execute('ROLLBACK TO SAVEPOINT check_negative_net_pay')
            if not self.env.context.get('from_batch_compute'):
                return {
                    'name': _('Negative Net Pay Warning'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'negative.net.pay.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': _("The following payslips have a negative net pay:\n%s\n\nDo you want to proceed and generate them?") % "\n".join([p.name for p in negative_slips]),
                        'default_payslip_ids': [(6, 0, self.ids)],
                        'default_is_batch': False,
                    }
                }
        else:
            self.env.cr.execute('RELEASE SAVEPOINT check_negative_net_pay')
            
        return res