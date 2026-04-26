{
    'name': 'HR Holiday Count',
    'version': '1.0',
    'category': 'Human Resources',
    'depends': ['payroll', 'resource'], # Add 'resource' here
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": True,
    'license': 'LGPL-3',
}