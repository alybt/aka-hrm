from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class BiometricDevice(models.Model):
    _name = 'biometric.device'
    _description = 'Biometric Device Configuration'
    _order = 'name'
    
    name = fields.Char(string='Device Name', required=True)
    device_type = fields.Selection([
        ('zkteco', 'ZKTeco'),
        ('hikvision', 'Hikvision'),
        ('suprema', 'Suprema'),
        ('custom', 'Custom Device')
    ], string='Device Type', required=True, default='zkteco')
    
    connection_type = fields.Selection([
        ('network', 'Network (IP)'),
        ('serial', 'Serial/USB'),
        ('http_api', 'HTTP API'),
        ('database', 'Database Import')
    ], string='Connection Type', required=True, default='network')
    
    # Network Configuration
    ip_address = fields.Char(string='IP Address')
    port = fields.Integer(string='Port', default=4370)
    api_key = fields.Char(string='API Key', help='Authentication key for API access')
    
    # Database Configuration
    database_name = fields.Char(string='Database Name')
    database_user = fields.Char(string='Database User')
    database_password = fields.Char(string='Database Password')
    database_host = fields.Char(string='Database Host')
    
    # Serial Configuration
    serial_port = fields.Char(string='Serial Port', default='COM1')
    baud_rate = fields.Integer(string='Baud Rate', default=9600)
    
    # Connection Settings
    timeout = fields.Integer(string='Connection Timeout (seconds)', default=30)
    is_active = fields.Boolean(string='Active', default=True)
    
    # Scheduling
    auto_sync = fields.Boolean(string='Auto Synchronization', default=False)
    sync_interval = fields.Selection([
        ('minutes', 'Minutes'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily')
    ], string='Sync Interval')
    
    last_connection = fields.Datetime(string='Last Successful Connection')
    connection_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')
    ], string='Connection Status', default='unknown')
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    
    def action_test_connection(self):
        """Test connection to biometric device"""
        self.ensure_one()
        
        try:
            if self.connection_type == 'network':
                # Test network connection
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.ip_address, self.port))
                sock.close()
                
                if result == 0:
                    self.connection_status = 'connected'
                    self.last_connection = fields.Datetime.now()
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Connection Successful',
                            'message': f'Successfully connected to {self.name} at {self.ip_address}:{self.port}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    self.connection_status = 'disconnected'
                    raise UserError(f'Could not connect to {self.ip_address}:{self.port}')
            
            elif self.connection_type == 'http_api':
                # Test HTTP API endpoint
                response = requests.get(
                    f'http://{self.ip_address}:{self.port}/api/status',
                    timeout=self.timeout,
                    headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
                )
                if response.status_code == 200:
                    self.connection_status = 'connected'
                    self.last_connection = fields.Datetime.now()
                else:
                    self.connection_status = 'error'
                    
            self.connection_status = 'connected'
            
        except Exception as e:
            self.connection_status = 'error'
            raise UserError(f'Connection test failed: {str(e)}')
    
    def action_import_attendance(self):
        """Trigger attendance import from this device"""
        return {
            'name': 'Import Attendance from Device',
            'type': 'ir.actions.act_window',
            'res_model': 'attendance.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_device_id': self.id},
        }