{
    'name': 'Payslip Contribution Checkbox',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Add contribution checkboxes in payslip',
    'description': """
        Add checkboxes in payslip to manually add government contributions
        even if not in salary structure.
    """,
    'author': 'Your Company',
    'depends': [
        'payroll',
        'contribution_manual',
    ],
    'data': [
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,

    'license': 'LGPL-3',
}