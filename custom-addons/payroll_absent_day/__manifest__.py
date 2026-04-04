{
    'name': 'Payroll Absent',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Count how many Absent/Undertime (Per Hour/ By Day)',
    'depends': ['base', 'resource', 'payroll', 'hr_holidays'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}