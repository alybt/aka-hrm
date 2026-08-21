from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BiometricAttendanceLog(models.Model):
    _name = 'biometric.attendance.log'
    _description = 'Biometric Attendance Log'
    _rec_name = 'employee_id'
    _order = 'attendance_time desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    device_id = fields.Many2one('biometric.device', string='Device', required=True, tracking=True)
    attendance_time = fields.Datetime(string='Attendance Time', required=True, default=fields.Datetime.now, tracking=True)

    attendance_type = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
    ], string='Type', required=True, tracking=True)

    verification_type = fields.Selection([
        ('fingerprint', 'Fingerprint'),
        ('password', 'Password'),
        ('card', 'RFID Card'),
    ], string='Verification Method', default='fingerprint')

    verified = fields.Boolean(string='Verified', default=True)
    sync_status = fields.Selection([
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
    ], string='Sync Status', default='pending', required=True, tracking=True)

    device_log_id = fields.Char(string='Device Log ID')
    attendance_id = fields.Many2one('hr.attendance', string='Related Attendance', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_sync_to_attendance(self):
        """Sync this log to hr.attendance"""
        for log in self.filtered(lambda x: x.sync_status == 'pending'):
            try:
                # Find or create attendance record
                attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', log.employee_id.id),
                    ('check_in', '<=', log.attendance_time),
                    ('check_out', '>=', log.attendance_time) if log.attendance_type == 'check_out' else ('check_out', '=', False)
                ], limit=1)

                if log.attendance_type == 'check_in':
                    if not attendance:
                        attendance = self.env['hr.attendance'].create({
                            'employee_id': log.employee_id.id,
                            'check_in': log.attendance_time,
                        })
                else:  # check_out
                    if attendance and not attendance.check_out:
                        attendance.write({'check_out': log.attendance_time})

                log.attendance_id = attendance.id
                log.sync_status = 'synced'

            except Exception as e:
                log.sync_status = 'failed'
                _logger.error(f"Failed to sync log {log.id}: {str(e)}")

    @api.model
    def _cron_sync_pending_logs(self):
        """Cron job to sync pending logs"""
        pending_logs = self.search([('sync_status', '=', 'pending')])
        pending_logs.action_sync_to_attendance()
        _logger.info(f"Synced {len(pending_logs)} attendance logs")