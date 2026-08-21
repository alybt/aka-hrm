{
    'name': 'Payroll OT Calculation',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Calculates Overtime Breakdown on Payslips',
    'depends': ['payroll', 'hr_worked_hours', 'hr_actual_work_days_count'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
        'installable': True,
    'application': True,
    "auto_install": False,
    'license': 'LGPL-3',
}