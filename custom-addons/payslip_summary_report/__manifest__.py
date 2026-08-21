{
    'name': 'Payslip Summary Report',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Tabular payslip summary report for batch printing',
    'depends': ['base', 'payroll'],
    'data': [
        'views/hr_payslip_views.xml',
        'reports/payslip_summary_report.xml',
        'reports/payslip_summary_template.xml',
    ],
    'installable': True,
}