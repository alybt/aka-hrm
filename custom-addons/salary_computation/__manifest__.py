{
    'name': 'Salary Computation',
    'version': '1.0',
    'category': 'Human Resources',
    'depends': ['hr', 'payroll'],
    'data': [
        'views/hr_payslip_view.xml',
        'views/time_bank.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": False,
    'license': 'LGPL-3',
}