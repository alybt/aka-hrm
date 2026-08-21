{
    'name': 'Biometric Attendance Management',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Attendance',
    'summary': 'Connect biometric devices to Odoo 17',
    'description': """
        Complete biometric device integration for Odoo 17.
        Features:
        - Connect and manage multiple biometric devices
        - Test device connection status
        - Register employees to biometric devices
        - Automatic attendance synchronization
        - Real-time attendance logging
    """,
    'author': 'Your Company',
    'website': 'https://yourcompany.com',
    'depends': ['base', 'hr_attendance', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/biometric_device_views.xml',
        'views/biometric_employee_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}