{
    'name': 'Biometric Attendance Integration',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Attendance',
    'summary': 'Integrate biometric devices with employee attendance',
    'description': """
        This module adds biometric integration capabilities to Odoo:
        - Biometric ID field on Employee form
        - Device configuration for biometric hardware
        - Attendance import from biometric exports
        - Support for multiple biometric device types
    """,
    'author': 'Your Company',
    'website': 'https://your-website.com',
    'depends': ['hr_attendance', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/biometric_device_views.xml',
        'views/attendance_import_views.xml',
        'data/demo_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}