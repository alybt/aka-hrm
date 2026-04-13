from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import pandas as pd
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AttendanceImport(models.Model):
    _name = 'attendance.import'
    _description = 'Attendance Import History'
    _rec_name = 'import_date'
    _order = 'import_date desc'
    
    import_date = fields.Datetime(string='Import Date', default=fields.Datetime.now, readonly=True)
    file_name = fields.Char(string='File Name')
    file_data = fields.Binary(string='File', attachment=True)
    device_id = fields.Many2one('biometric.device', string='Biometric Device')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], string='Status', default='draft')
    
    total_records = fields.Integer(string='Total Records', readonly=True)
    success_records = fields.Integer(string='Successfully Imported', readonly=True)
    failed_records = fields.Integer(string='Failed Records', readonly=True)
    
    error_log = fields.Text(string='Error Log', readonly=True)
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    def action_process_import(self):
        """Process the imported attendance file"""
        self.ensure_one()
        self.status = 'processing'
        
        try:
            # Decode the file
            file_content = base64.b64decode(self.file_data)
            
            # Determine file type and parse
            if self.file_name.endswith('.csv'):
                df = pd.read_csv(file_content)
            elif self.file_name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_content)
            else:
                raise UserError('Unsupported file format. Please use CSV or Excel files.')
            
            self.total_records = len(df)
            success_count = 0
            error_messages = []
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    self._process_attendance_record(row, index)
                    success_count += 1
                except Exception as e:
                    error_messages.append(f"Row {index + 1}: {str(e)}")
            
            self.success_records = success_count
            self.failed_records = self.total_records - success_count
            
            if error_messages:
                self.error_log = '\n'.join(error_messages)
            
            self.status = 'completed'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Import Complete',
                    'message': f'Successfully imported {success_count} out of {self.total_records} attendance records',
                    'type': 'success' if success_count > 0 else 'warning',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            self.status = 'failed'
            self.error_log = str(e)
            raise UserError(f'Import failed: {str(e)}')
    
    def _process_attendance_record(self, row, row_index):
        """Process a single attendance record"""
        # Map expected columns (customize based on your device)
        biometric_id = str(row.get('UserID') or row.get('EmployeeID') or row.get('BiometricID', ''))
        check_time = row.get('DateTime') or row.get('CheckTime') or row.get('Timestamp')
        
        if not biometric_id or not check_time:
            raise ValueError('Missing required fields: Biometric ID or Check Time')
        
        # Find employee by biometric ID
        employee = self.env['hr.employee'].search([
            ('biometric_id', '=', biometric_id),
            ('biometric_enabled', '=', True)
        ], limit=1)
        
        if not employee:
            raise ValueError(f'Employee with biometric ID {biometric_id} not found')
        
        # Parse datetime
        if isinstance(check_time, str):
            check_datetime = datetime.strptime(check_time, '%Y-%m-%d %H:%M:%S')
        else:
            check_datetime = check_time
        
        # Check for existing attendance
        existing = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '<=', check_datetime),
            ('check_out', '>=', check_datetime)
        ], limit=1)
        
        if existing:
            _logger.info(f"Attendance record already exists for {employee.name} at {check_datetime}")
            return
        
        # Determine if this is check-in or check-out based on the day's records
        day_attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', check_datetime.date()),
            ('check_in', '<', check_datetime.date() + timedelta(days=1))
        ], order='check_in')
        
        if len(day_attendances) % 2 == 0:
            # Even number of records - this should be a check-in
            self.env['hr.attendance'].create({
                'employee_id': employee.id,
                'check_in': check_datetime,
                'check_out': False,
            })
        else:
            # Odd number - this should be a check-out, find the last open record
            last_attendance = day_attendances.filtered(lambda a: not a.check_out)[-1:] if day_attendances else None
            if last_attendance:
                last_attendance.write({'check_out': check_datetime})