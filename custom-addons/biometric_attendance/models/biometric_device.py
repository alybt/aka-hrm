from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class BiometricDevice(models.Model):
    _name = 'biometric.device'
    _description = 'Biometric Fingerprint Device'
    _rec_name = 'device_name'
    _order = 'device_name'

    device_name = fields.Char(string='Device Name', required=True)
    device_ip = fields.Char(string='Device IP Address', required=True)
    device_port = fields.Integer(string='Device Port', default=4370)
    device_model = fields.Selection([
        ('zkteco', 'ZK Teco'),
        ('secugen', 'SecuGen'),
        ('digital_persona', 'Digital Persona'),
        ('other', 'Other'),
    ], string='Device Model', required=True, default='zkteco')
    
    device_serial = fields.Char(string='Device Serial Number')
    device_status = fields.Selection([
        ('draft', 'Draft'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ], string='Device Status', default='draft', required=True)
    
    last_sync = fields.Datetime(string='Last Synchronization')
    total_users = fields.Integer(string='Total Registered Users', compute='_compute_total_users')
    
    company_id = fields.Many2one('res.company', string='Company', 
                                 default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)
    
    # Device configuration
    device_timeout = fields.Integer(string='Connection Timeout (sec)', default=5)
    retry_attempts = fields.Integer(string='Retry Attempts', default=3)
    
    # Advanced settings
    auto_sync = fields.Boolean(string='Auto Synchronize', default=True)
    sync_interval = fields.Integer(string='Sync Interval (minutes)', default=5)
    
    @api.depends('device_name')
    def _compute_total_users(self):
        for device in self:
            device.total_users = self.env['biometric.user'].search_count([
                ('device_id', '=', device.id)
            ])
    
    @api.constrains('device_ip')
    def _check_device_ip(self):
        for device in self:
            if device.device_ip:
                parts = device.device_ip.split('.')
                if len(parts) != 4:
                    raise ValidationError(_("Invalid IP address format"))
                for part in parts:
                    if not part.isdigit() or int(part) < 0 or int(part) > 255:
                        raise ValidationError(_("Invalid IP address range"))
    
    def action_test_connection(self):
        """Test connection to biometric device"""
        self.ensure_one()
        # Here you would implement actual device communication
        # This is a placeholder for actual SDK integration
        try:
            # Simulate connection test
            self.device_status = 'connected'
            self.last_sync = fields.Datetime.now()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection Test'),
                    'message': _('Successfully connected to device %s') % self.device_name,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.device_status = 'error'
            raise ValidationError(_("Connection failed: %s") % str(e))
    
    def action_sync_users(self):
        """Synchronize users from device to Odoo"""
        self.ensure_one()
        # Implement user synchronization logic
        # This would read fingerprint templates from the device
        pass
    
    def action_sync_attendance(self):
        """Synchronize attendance logs from device"""
        self.ensure_one()
        # Implement attendance log synchronization
        pass