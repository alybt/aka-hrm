from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    biometric_registrations = fields.One2many('biometric.employee', 'employee_id', string='Biometric Registrations')
    has_biometric = fields.Boolean(string='Has Biometric Access', compute='_compute_has_biometric', store=True)
    biometric_enrolled = fields.Boolean(string='Biometric Enrolled', compute='_compute_has_biometric', store=True)

    @api.depends('biometric_registrations', 'biometric_registrations.status')
    def _compute_has_biometric(self):
        for employee in self:
            registered = employee.biometric_registrations.filtered(lambda x: x.status == 'registered')
            employee.has_biometric = bool(registered)
            employee.biometric_enrolled = bool(registered)

    def action_register_biometric(self):
        """Open wizard to register employee for biometrics"""
        return {
            'name': _('Register for Biometric Device'),
            'type': 'ir.actions.act_window',
            'res_model': 'biometric.registration.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_employee_name': self.name,
            }
        }