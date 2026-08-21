from odoo import models, fields, api, _

class BiometricRegistrationWizard(models.TransientModel):
    _name = 'biometric.registration.wizard'
    _description = 'Biometric Registration Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    employee_name = fields.Char(string='Employee Name', related='employee_id.name', readonly=True)
    device_id = fields.Many2one('biometric.device', string='Device', required=True,
                                domain="[('device_status', '=', 'connected'), ('active', '=', True)]")
    user_id_in_device = fields.Integer(string='Device User ID', required=True,
                                       help='Unique ID for this employee on the device')

    def action_register(self):
        """Register employee on the selected device"""
        existing = self.env['biometric.employee'].search([
            ('employee_id', '=', self.employee_id.id),
            ('device_id', '=', self.device_id.id)
        ])

        if existing:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Already Registered'),
                    'message': _('This employee is already registered on this device.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        biometric_employee = self.env['biometric.employee'].create({
            'employee_id': self.employee_id.id,
            'device_id': self.device_id.id,
            'user_id_in_device': self.user_id_in_device,
            'status': 'pending',
        })

        # Attempt to register on device
        biometric_employee.action_register_on_device()

        return {'type': 'ir.actions.act_window_close'}