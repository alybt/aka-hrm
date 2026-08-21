{
    'name': 'Actual Days Breakdown by Holiday Type',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Count calendar days broken down by Philippine holiday types',
    'depends': ['payroll'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": False,
    'license': 'LGPL-3',
}