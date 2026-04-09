from odoo import models, fields, api, _
from datetime import timedelta

class BiometricAttendanceLog(models.Model):
    _name = 'biometric.attendance.log'
    _description = 'Biometric Attendance Log'
    _rec_name = 'employee_id'
    _order = 'attendance_time desc'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    device_id = fields.Many2one('biometric.device', string='Device', required=True)
    attendance_time = fields.Datetime(string='Attendance Time', required=True, default=fields.Datetime.now)
    
    attendance_type = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string='Attendance Type', required=True)
    
    verification_type = fields.Selection([
        ('fingerprint', 'Fingerprint'),
        ('manual', 'Manual Entry'),
        ('card', 'RFID Card'),
    ], string='Verification Method', default='fingerprint')
    
    verified = fields.Boolean(string='Verified', default=True)
    sync_status = fields.Selection([
        ('synced', 'Synced'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ], string='Sync Status', default='pending')
    
    device_log_id = fields.Char(string='Device Log ID')
    company_id = fields.Many2one('res.company', string='Company', 
                                    default=lambda self: self.env.company)
    
    @api.model
    def create_attendance_from_device(self, employee_id, timestamp, attendance_type):
        """Create attendance record from device data"""
        employee = self.env['hr.employee'].browse(employee_id)
        
        # Find or create attendance record
        attendance_obj = self.env['hr.attendance']
        
        # Check if already checked in/out
        today = fields.Date.today()
        existing = attendance_obj.search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', today),
            ('check_out', '=', False)
        ], limit=1)
        
        if attendance_type == 'check_in':
            if not existing:
                attendance_obj.create({
                    'employee_id': employee.id,
                    'check_in': timestamp,
                })
        else:  # check_out
            if existing:
                existing.write({'check_out': timestamp})
        
        return True
    
    @api.model
    def _cron_sync_pending_logs(self):
        """Cron job to sync pending logs to attendance"""
        pending_logs = self.search([('sync_status', '=', 'pending')])
        for log in pending_logs:
            try:
                log.create_attendance_from_device(
                    log.employee_id.id,
                    log.attendance_time,
                    log.attendance_type
                )
                log.sync_status = 'synced'
            except Exception as e:
                log.sync_status = 'failed'
                _logger.error(f"Failed to sync log {log.id}: {str(e)}")