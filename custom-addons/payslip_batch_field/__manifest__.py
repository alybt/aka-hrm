{
    'name': 'Batch Payslip Fields',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Additional computed fields for batch payslips',
    'description': """
        Add computed fields to batch payslip tree view:
        - Total Hours: (working_days * 8) - undertime_hrs
        - Hourly Rate: daily_rate / 8
        - Undertime Cost: undertime_hrs * hourly_rate
        - Gross Pay: regular + holiday pays
    """,
    'author': 'Your Company',
    'depends': ['payroll', 'hr'],
    'data': [
        'views/hr_payslip_run_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}