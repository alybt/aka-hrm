{
    'name': 'Overtime to Time Bank',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Add overtime from payslips to employee time bank',
    'depends': ['hr', 'payroll'],
    'data': [
        'views/hr_employee_view.xml',
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}