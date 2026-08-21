from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BiometricEmployee(models.Model):
    _name = 'biometric.employee'
    _description = 'Biometric Employee Registration'
    _rec_name = 'employee_id'
    _order = 'registration_date desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    device_id = fields.Many2one('biometric.device', string='Device', required=True, ondelete='cascade')

    user_id_in_device = fields.Integer(string='Device User ID', help='User ID as stored in the biometric device')
    fingerprint_count = fields.Integer(string='Registered Fingerprints', default=0)

    status = fields.Selection([
        ('pending', 'Pending Registration'),
        ('registered', 'Registered'),
        ('failed', 'Registration Failed'),
    ], string='Status', default='pending', required=True)

    registration_date = fields.Datetime(string='Registration Date')
    last_verification = fields.Datetime(string='Last Verification')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_employee_device', 'unique(employee_id, device_id)', 'An employee can only be registered once per device!'),
        ('unique_device_user_id', 'unique(device_id, user_id_in_device)', 'User ID must be unique per device!')
    ]

    def action_register_on_device(self):
        """Register employee on the biometric device"""
        self.ensure_one()

        if not self.user_id_in_device:
            raise UserError(_('Please set a Device User ID before registering.'))

        try:
            # Here you would implement actual device registration
            # This is a placeholder for actual SDK integration

            self.status = 'registered'
            self.registration_date = fields.Datetime.now()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Registration Successful'),
                    'message': _('Employee %s has been registered on device %s') % (self.employee_id.name, self.device_id.name),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.status = 'failed'
            raise UserError(_('Registration failed: %s') % str(e))

    def action_remove_from_device(self):
        """Remove employee from biometric device"""
        self.ensure_one()

        try:
            # Here you would implement device removal logic

            self.unlink()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Removal Successful'),
                    'message': _('Employee has been removed from device'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise UserError(_('Removal failed: %s') % str(e))