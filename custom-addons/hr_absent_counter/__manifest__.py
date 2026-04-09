{
    'name': 'HR Absence Counter',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Count employee absences excluding holidays',
    'description': """
        This module counts employee absences from work schedule
        while excluding configured holiday types from being counted as absences.
        
        Holiday Types excluded:
        - Regular Holiday
        - Special Non-Working Holiday  
        - Special Working Holiday
        - Local Holiday
    """,
    'author': 'AKA',
    'website': '',
    'depends': ['hr', 'hr_holidays', 'hr_attendance', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_absence_count_views.xml',
        'data/absence_count_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}