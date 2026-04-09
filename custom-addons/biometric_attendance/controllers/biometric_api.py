from odoo import http
from odoo.http import request
import json
from datetime import datetime

class BiometricAPI(http.Controller):
    
    @http.route('/api/biometric/attendance', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_attendance(self, **kwargs):
        """API endpoint for biometric devices to send attendance data"""
        # Validate API key/device authentication
        api_key = request.httprequest.headers.get('X-API-Key')
        device_serial = request.jsonrequest.get('device_serial')
        
        device = request.env['biometric.device'].sudo().search([
            ('device_serial', '=', device_serial),
            ('device_status', '=', 'connected')
        ], limit=1)
        
        if not device:
            return {'status': 'error', 'message': 'Invalid device'}
        
        # Process attendance data
        attendance_data = request.jsonrequest.get('attendance', [])
        
        for record in attendance_data:
            # Find employee by fingerprint ID or user code
            employee = request.env['hr.employee'].sudo().search([
                ('biometric_user_ids.user_id_in_device', '=', record.get('user_id'))
            ], limit=1)
            
            if employee:
                request.env['biometric.attendance.log'].sudo().create({
                    'employee_id': employee.id,
                    'device_id': device.id,
                    'attendance_time': datetime.fromtimestamp(record.get('timestamp')),
                    'attendance_type': record.get('type', 'check_in'),
                    'device_log_id': record.get('log_id'),
                    'sync_status': 'synced'
                })
        
        return {'status': 'success', 'message': f'Processed {len(attendance_data)} records'}
    
    @http.route('/api/biometric/register', type='json', auth='user', methods=['POST'])
    def register_fingerprint(self, **kwargs):
        """Register fingerprint template from client"""
        # Implementation for registering fingerprints via API
        pass