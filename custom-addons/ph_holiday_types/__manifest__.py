{
    'name': 'Philippines Public Holiday Types',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Categorize Public Holidays as Regular, Special, or Local.',
    'depends': ['base', 'resource', 'hr_holidays'],
    'data': [
        'views/resource_calendar_leaves_views.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    'license': 'LGPL-3',
}