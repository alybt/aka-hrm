{
    'name': 'Salary Computation',
    'version': '1.0',
    'category': 'Human Resources',
    'depends': [ 'base', 'hr', 'payroll','hr_holidays', 'hr_attendance', 'hr_expense' ],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": False,
    'license': 'LGPL-3',
}