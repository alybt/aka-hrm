{
    'name': 'Time Off Leave Overtime Fix',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Fix missing overtime_deductible field in Time Off Management',
    'description': """
        This module adds the missing overtime_deductible field to
        hr.leave model to prevent errors in Time Off Management.
    """,
    'author': 'Your Company',
    'depends': ['hr_holidays'],
    'data': [
        'views/hr_leave_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}