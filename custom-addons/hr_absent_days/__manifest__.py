{
    'name': 'HR Absent Days',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Absent Day within the span',
    'depends': ['payroll', 'hr_work_entry','hr_holidays', 'resource', ],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    "auto_install": True,
    'license': 'LGPL-3',
}
