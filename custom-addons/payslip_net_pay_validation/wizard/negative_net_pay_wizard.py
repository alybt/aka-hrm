from odoo import api, fields, models, _

class NegativeNetPayWizard(models.TransientModel):
    _name = 'negative.net.pay.wizard'
    _description = 'Negative Net Pay Warning Wizard'

    message = fields.Text(string="Message", readonly=True)
    payslip_ids = fields.Many2many('hr.payslip', string="Payslips")
    batch_id = fields.Many2one('hr.payslip.run', string="Batch")
    is_batch = fields.Boolean(string="Is Batch")

    def action_confirm(self):
        """Proceed with generation despite negative net pay"""
        self.ensure_one()
        if self.is_batch and self.batch_id:
            return self.batch_id.with_context(ignore_negative_net_pay=True).action_batch_compute()
        elif self.payslip_ids:
            for payslip in self.payslip_ids:
                payslip.with_context(ignore_negative_net_pay=True).compute_sheet()
            return {'type': 'ir.actions.act_window_close'}
