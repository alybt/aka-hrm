{
    'name': 'HR Undertime',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Calculate Undertime Hours and Days for Employees',
    'depends': ['payroll', 'hr_attendance'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    'license': 'LGPL-3',
}