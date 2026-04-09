from odoo import models, fields, api, _
import base64

class BiometricUser(models.Model):
    _name = 'biometric.user'
    _description = 'Biometric User Registration'
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    device_id = fields.Many2one('biometric.device', string='Device', required=True)
    
    fingerprint_templates = fields.Binary(string='Fingerprint Templates', attachment=True)
    fingerprint_count = fields.Integer(string='Registered Fingerprints', default=0)
    user_id_in_device = fields.Integer(string='Device User ID')
    
    registration_status = fields.Selection([
        ('pending', 'Pending'),
        ('registered', 'Registered'),
        ('failed', 'Registration Failed'),
    ], string='Status', default='pending')
    
    registration_date = fields.Datetime(string='Registration Date')
    last_verification = fields.Datetime(string='Last Verification')
    
    # Fingerprint details
    finger_1_template = fields.Binary(string='Finger 1 Template', attachment=True)
    finger_2_template = fields.Binary(string='Finger 2 Template', attachment=True)
    finger_3_template = fields.Binary(string='Finger 3 Template', attachment=True)
    
    company_id = fields.Many2one('res.company', string='Company', 
                                    default=lambda self: self.env.company)
    
    _sql_constraints = [
        ('unique_employee_device', 'unique(employee_id, device_id)', 
            'Employee can only be registered once per device!')
    ]
    
    def action_register_fingerprints(self):
        """Register fingerprints on the biometric device"""
        self.ensure_one()
        # This would communicate with the device SDK to enroll fingerprints
        pass
    
    def action_verify_fingerprint(self):
        """Verify fingerprint match"""
        self.ensure_one()
        # Implement fingerprint verification logic
        pass