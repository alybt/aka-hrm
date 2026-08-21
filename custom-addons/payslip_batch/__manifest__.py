{
    'name': 'Batch Payslip Actions',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Batch operations for payslip runs',
    'description': """
        Add batch actions for payslip runs:
        - Confirm all payslips
        - Compute all payslips
        - Set all to Draft
        - Cancel all payslips
        - Refetch data for all payslips
    """,
    'author': 'Your Company',
    'depends': ['payroll', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_run_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}