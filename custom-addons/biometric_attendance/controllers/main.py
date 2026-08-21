from odoo import http
from odoo.http import request
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class BiometricController(http.Controller):

    @http.route('/api/biometric/attendance', type='json', auth='public', methods=['POST'], csrf=False)
    def receive_attendance(self):
        """API endpoint for biometric devices to send attendance data"""
        try:
            # Get API key from header
            api_key = request.httprequest.headers.get('X-API-Key')

            # Validate device
            device_serial = request.jsonrequest.get('device_serial')
            device = request.env['biometric.device'].sudo().search([
                ('device_serial', '=', device_serial),
                ('device_status', 'in', ['connected', 'draft'])
            ], limit=1)

            if not device:
                return {'status': 'error', 'message': 'Invalid device or API key'}

            # Process attendance data
            attendance_data = request.jsonrequest.get('attendance', [])
            processed = 0

            for record in attendance_data:
                # Find biometric employee
                biometric_emp = request.env['biometric.employee'].sudo().search([
                    ('user_id_in_device', '=', record.get('user_id')),
                    ('device_id', '=', device.id)
                ], limit=1)

                if biometric_emp and biometric_emp.employee_id:
                    # Check if log already exists
                    existing = request.env['biometric.attendance.log'].sudo().search([
                        ('device_log_id', '=', record.get('log_id')),
                        ('device_id', '=', device.id)
                    ], limit=1)

                    if not existing:
                        request.env['biometric.attendance.log'].sudo().create({
                            'employee_id': biometric_emp.employee_id.id,
                            'device_id': device.id,
                            'attendance_time': datetime.fromtimestamp(record.get('timestamp')),
                            'attendance_type': record.get('type', 'check_in'),
                            'device_log_id': record.get('log_id'),
                            'sync_status': 'pending',
                        })
                        processed += 1

            return {
                'status': 'success',
                'message': f'Processed {processed} records',
                'processed': processed
            }

        except Exception as e:
            _logger.error(f"Error processing attendance: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/biometric/device/status', type='json', auth='public', methods=['GET'], csrf=False)
    def device_status(self):
        """Check device status"""
        device_serial = request.params.get('device_serial')
        device = request.env['biometric.device'].sudo().search([
            ('device_serial', '=', device_serial)
        ], limit=1)

        if device:
            return {
                'status': 'ok',
                'device_name': device.name,
                'device_status': device.device_status,
                'last_sync': device.last_sync.strftime('%Y-%m-%d %H:%M:%S') if device.last_sync else None
            }
        return {'status': 'error', 'message': 'Device not found'}