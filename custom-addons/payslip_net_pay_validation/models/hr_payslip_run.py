from odoo import models, _

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_batch_compute(self):
        if self.env.context.get('ignore_negative_net_pay'):
            return super().action_batch_compute()

        self.env.cr.execute('SAVEPOINT batch_compute_savepoint')
        
        # We need to compute to see the results.
        # We pass from_batch_compute to prevent individual slips from returning the wizard.
        res = super(HrPayslipRun, self.with_context(from_batch_compute=True)).action_batch_compute()
        
        payslips = self.slip_ids.filtered(lambda p: p.state in ['draft', 'verify'])
        negative_slips = payslips.filtered(lambda p: p.x_net_pay < 0)
        
        if negative_slips:
            self.env.cr.execute('ROLLBACK TO SAVEPOINT batch_compute_savepoint')
            return {
                'name': _('Negative Net Pay Warning'),
                'type': 'ir.actions.act_window',
                'res_model': 'negative.net.pay.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_message': _("The following payslips in this batch have a negative net pay:\n%s\n\nDo you want to proceed and generate them?") % "\n".join([p.name for p in negative_slips]),
                    'default_batch_id': self.id,
                    'default_is_batch': True,
                }
            }
        else:
            self.env.cr.execute('RELEASE SAVEPOINT batch_compute_savepoint')
            
        return res
