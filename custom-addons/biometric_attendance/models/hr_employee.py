from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    biometric_user_ids = fields.One2many('biometric.user', 'employee_id', string='Biometric Registrations')
    has_biometric = fields.Boolean(string='Has Biometric Registration', compute='_compute_has_biometric')
    
    @api.depends('biometric_user_ids')
    def _compute_has_biometric(self):
        for employee in self:
            employee.has_biometric = bool(employee.biometric_user_ids.filtered(
                lambda u: u.registration_status == 'registered'
            ))
    
    def action_register_biometric(self):
        """Open wizard to register employee for biometrics"""
        return {
            'name': 'Register Biometric',
            'type': 'ir.actions.act_window',
            'res_model': 'biometric.user.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }