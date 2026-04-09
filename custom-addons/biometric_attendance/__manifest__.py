{
    'name': 'Biometric Fingerprint Attendance',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Attendance',
    'summary': 'Biometric fingerprint scanner integration for employee attendance',
    'description': """
        This module integrates biometric fingerprint devices with Odoo Attendance.
        Features:
        - Support for multiple fingerprint devices
        - Real-time attendance logging
        - Fingerprint template management
        - Automatic attendance calculation
        - Device synchronization
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'hr_attendance', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/biometric_device_view.xml',
        'views/biometric_attendance_view.xml',
        'views/hr_employee_view.xml',
        'data/biometric_cron.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}