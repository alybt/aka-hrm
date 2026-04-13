from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    biometric_id = fields.Char(
        string='Biometric ID',
        help='Unique identifier from biometric device',
        copy=False,
        index=True
    )
    
    biometric_enabled = fields.Boolean(
        string='Biometric Access Enabled',
        default=True,
        help='Enable biometric attendance for this employee'
    )
    
    biometric_device_ids = fields.Many2many(
        'biometric.device',
        string='Registered Devices',
        help='Biometric devices where this employee is registered'
    )
    
    last_biometric_sync = fields.Datetime(
        string='Last Biometric Sync',
        readonly=True
    )
    
    biometric_verification_method = fields.Selection([
        ('fingerprint', 'Fingerprint'),
        ('face', 'Face Recognition'),
        ('card', 'RFID Card'),
        ('pin', 'PIN Code'),
        ('multi', 'Multi-Factor')
    ], string='Verification Method', default='fingerprint')
    
    @api.constrains('biometric_id')
    def _check_biometric_id(self):
        for employee in self:
            if employee.biometric_id:
                existing = self.search([
                    ('biometric_id', '=', employee.biometric_id),
                    ('id', '!=', employee.id)
                ])
                if existing:
                    raise ValidationError(
                        f'Biometric ID {employee.biometric_id} is already assigned '
                        f'to employee {existing[0].name}'
                    )
    
    def action_sync_biometric_data(self):
        """Manual sync button action"""
        for employee in self:
            employee.last_biometric_sync = fields.Datetime.now()
            # Trigger sync logic here
            _logger.info(f"Synced biometric data for employee {employee.name}")
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Biometric data sync initiated',
                'type': 'rainbow_man',
            }
        }