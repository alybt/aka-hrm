{
    'name': 'Total Worked Hours',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Daily Rate',
    'depends': ['payroll'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": True,
    'license': 'LGPL-3',
}