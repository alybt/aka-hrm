# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Expense Payroll Integration',
    'version': '1.0.0',
    'category': 'Human Resources/Expenses',
    'summary': 'Integrate expense reimbursements with payroll',
    'description': """
HR Expense Payroll Integration
==============================

This module allows expense reimbursements to be processed through payroll instead of direct payments.

Features:
* Add "Include in Payroll" option to expense sheets
* Bypass payment processing for payroll-included expenses
* Mark expenses as paid through payroll system
* Track payroll-reimbursed expenses separately
    """,
    'author': 'Your Company',
    'depends': ['hr_expense', 'payroll', 'payroll_account'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_expense_payroll_data.xml',
        'views/hr_expense_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
