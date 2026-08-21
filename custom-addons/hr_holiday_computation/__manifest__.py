{
    'name': 'Holiday Computation',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Compute Regular, Special Non-Working, and Special Working Holiday Rates',
    'description': """
        Module for computing holiday rates based on:
        - Actual Regular Holiday
        - Actual Special Non-Working Holiday
        - Actual Special Working Holiday
        - Daily Salary
    """,
    'author': 'Your Company',
    'depends': ['base', 'hr', 'payroll', 'hr_actual_work_days_count', 'hr_salary_daily', 'hr_worked_hours'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

    'license': 'LGPL-3',
}