from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _get_available_batch_actions(self):
        """Get available batch actions based on payslip state"""
        actions = []

        if self.state == 'draft':
            actions.extend(['confirm', 'compute', 'refetch'])
        elif self.state == 'verify':
            actions.extend(['compute', 'confirm'])
        elif self.state == 'cancel':
            actions.extend(['draft'])
        elif self.state == 'done':
            if not self.paid:
                actions.extend(['cancel'])

        return actions