{
    'name': 'Philippine Employee Government IDs',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Philippine Government IDs for Employees',
    'description': """
        This module adds Philippine government ID management for employees:
        - SSS Number (Social Security System)
        - PhilHealth Number
        - Pag-IBIG MID Number
        - TIN Number (Tax Identification Number)

        Features:
        - Automatic number formatting
        - Validation of correct format
        - Support for multiple ID records per employee
        - Active/Inactive status for tracking old IDs
    """,
    'author': 'Your Company',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/ph_employee_ids_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}