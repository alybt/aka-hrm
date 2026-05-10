{
    'name': 'Philippine Company IDs',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Adds Philippine company IDs with input masking',
    'description': """
        Adds SSS Employer, TIN, PhilHealth, and Pag-IBIG fields to company form
        with automatic formatting and character limits.
    """,
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}