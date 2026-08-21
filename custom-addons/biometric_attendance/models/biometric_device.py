from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    from zklib import ZK
    ZK_AVAILABLE = True
except ImportError:
    ZK_AVAILABLE = False
    _logger.warning("python-zklib not installed. Device connection will be simulated.")

class BiometricDevice(models.Model):
    _name = 'biometric.device'
    _description = 'Biometric Device'
    _rec_name = 'name'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Device Name', required=True, tracking=True)
    device_ip = fields.Char(string='IP Address', required=True, tracking=True)
    device_port = fields.Integer(string='Port', default=4370, required=True, tracking=True)
    device_model = fields.Selection([
        ('zkteco', 'ZK Teco'),
        ('secugen', 'SecuGen'),
        ('other', 'Other'),
    ], string='Device Model', required=True, default='zkteco', tracking=True)

    device_serial = fields.Char(string='Serial Number', readonly=True, tracking=True)
    device_status = fields.Selection([
        ('draft', 'Draft'),
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error'),
    ], string='Status', default='draft', required=True, tracking=True)

    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    total_users = fields.Integer(string='Total Users', compute='_compute_total_users', store=False)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)

    # Connection settings
    connection_timeout = fields.Integer(string='Timeout (seconds)', default=5, help='Connection timeout in seconds')

    # Sync settings
    auto_sync = fields.Boolean(string='Auto Sync', default=True, help='Automatically sync attendance logs')
    sync_interval = fields.Integer(string='Sync Interval (minutes)', default=5, help='Interval between automatic syncs')

    # Statistics
    total_employees = fields.Integer(string='Registered Employees', compute='_compute_employees_count', store=False)
    today_attendance = fields.Integer(string="Today's Attendance", compute='_compute_today_attendance', store=False)

    biometric_employee_ids = fields.One2many('biometric.employee', 'device_id', string='Registered Employees')

    @api.depends('biometric_employee_ids')
    def _compute_total_users(self):
        for device in self:
            device.total_users = len(device.biometric_employee_ids.filtered(lambda x: x.status == 'registered'))

    def _compute_employees_count(self):
        for device in self:
            device.total_employees = len(device.biometric_employee_ids)

    def _compute_today_attendance(self):
        for device in self:
            today = fields.Date.today()
            device.today_attendance = self.env['biometric.attendance.log'].search_count([
                ('device_id', '=', device.id),
                ('attendance_time', '>=', today)
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

        if not ZK_AVAILABLE and self.device_model == 'zkteco':
            raise UserError(_('python-zklib library is not installed. Please install it with: pip install python-zklib'))

        try:
            if self.device_model == 'zkteco' and ZK_AVAILABLE:
                # Real ZKTeco connection
                zk = ZK(self.device_ip, self.device_port, timeout=self.connection_timeout)
                conn = zk.connect()

                if conn:
                    device_info = conn.get_device_info()
                    self.device_serial = device_info.get('serial_number', '')
                    self.device_status = 'connected'
                    self.last_sync = fields.Datetime.now()
                    conn.disconnect()

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Connection Successful'),
                            'message': _('Successfully connected to device: %s\nSerial: %s') % (self.name, self.device_serial),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
            else:
                # Simulated connection for testing
                self.device_status = 'connected'
                self.device_serial = f'SIM-{datetime.now().strftime("%Y%m%d%H%M%S")}'
                self.last_sync = fields.Datetime.now()

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful (Simulated)'),
                        'message': _('Successfully connected to device: %s\nNote: This is a simulated connection for testing.') % self.name,
                        'type': 'success',
                        'sticky': False,
                    }
                }

        except Exception as e:
            self.device_status = 'error'
            raise UserError(_('Connection failed: %s') % str(e))

    def action_sync_employees(self):
        """Sync employees from device to Odoo"""
        self.ensure_one()

        try:
            if self.device_model == 'zkteco' and ZK_AVAILABLE:
                zk = ZK(self.device_ip, self.device_port, timeout=self.connection_timeout)
                conn = zk.connect()

                if conn:
                    users = conn.get_users()
                    for user in users:
                        # Find or create employee based on user_id
                        employee = self.env['hr.employee'].search([
                            ('identification_id', '=', str(user.uid))
                        ], limit=1)

                        if employee:
                            # Register biometric link
                            existing = self.env['biometric.employee'].search([
                                ('employee_id', '=', employee.id),
                                ('device_id', '=', self.id)
                            ], limit=1)

                            if not existing:
                                self.env['biometric.employee'].create({
                                    'employee_id': employee.id,
                                    'device_id': self.id,
                                    'user_id_in_device': user.uid,
                                    'status': 'registered',
                                    'registration_date': fields.Datetime.now(),
                                })

                    conn.disconnect()
                    self.last_sync = fields.Datetime.now()

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Sync Completed'),
                            'message': _('Successfully synced employees from device'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }

            # Simulated sync for testing
            self.last_sync = fields.Datetime.now()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Completed (Simulated)'),
                    'message': _('Employee sync completed (simulated mode)'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            raise UserError(_('Sync failed: %s') % str(e))

    def action_sync_attendance(self):
        """Sync attendance logs from device"""
        self.ensure_one()

        try:
            if self.device_model == 'zkteco' and ZK_AVAILABLE:
                zk = ZK(self.device_ip, self.device_port, timeout=self.connection_timeout)
                conn = zk.connect()

                if conn:
                    logs = conn.get_attendance()
                    count = 0

                    for log in logs:
                        # Find biometric employee
                        biometric_emp = self.env['biometric.employee'].search([
                            ('user_id_in_device', '=', log.user_id),
                            ('device_id', '=', self.id)
                        ], limit=1)

                        if biometric_emp and biometric_emp.employee_id:
                            # Check if log already exists
                            existing = self.env['biometric.attendance.log'].search([
                                ('device_log_id', '=', str(log.uid)),
                                ('device_id', '=', self.id)
                            ], limit=1)

                            if not existing:
                                # Create attendance log
                                attendance_time = fields.Datetime.from_string(str(log.timestamp))
                                attendance_type = 'check_in' if log.punch == 0 else 'check_out'

                                self.env['biometric.attendance.log'].create({
                                    'employee_id': biometric_emp.employee_id.id,
                                    'device_id': self.id,
                                    'attendance_time': attendance_time,
                                    'attendance_type': attendance_type,
                                    'device_log_id': str(log.uid),
                                    'sync_status': 'synced',
                                })
                                count += 1

                    conn.disconnect()
                    self.last_sync = fields.Datetime.now()

                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Attendance Sync Completed'),
                            'message': _('Successfully synced %d attendance records') % count,
                            'type': 'success',
                            'sticky': False,
                        }
                    }

            # Simulated sync for testing
            self.last_sync = fields.Datetime.now()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Attendance Sync Completed (Simulated)'),
                    'message': _('Attendance sync completed (simulated mode)'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            raise UserError(_('Attendance sync failed: %s') % str(e))