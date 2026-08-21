{
    'name': 'Payslip Net Pay Validation',
    'version': '1.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Prevents confirming a payslip with negative net pay',
    'depends': ['payroll', 'payslip_batch'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/negative_net_pay_wizard_views.xml',
    ],
    'installable': True,
}