{
    'name': 'Expense Reimbursement in Payslip',
    'version': '1.0',
    'depends': ['payroll', 'hr_expense'],
    'data': [
        'views/hr_payslip_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    'license': 'LGPL-3',
}
