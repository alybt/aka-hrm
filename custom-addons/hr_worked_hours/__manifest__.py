{
    'name': 'Work Hours Breakdown by Holiday Type',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Breakdown work hours based on Philippine holiday types from work entries',
    'depends': ['payroll', 'hr_holidays', 'hr_attendance'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": False,
    'license': 'LGPL-3',
}