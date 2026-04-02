{
    'name': 'Philippines Holiday Types Extension',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Adds Regular, Special, and Local holiday types for PH Payroll.',
    "license": "AGPL-3",
    'depends': [
        'resource', 
        'hr_work_entry', 
        'hr_holidays'],
    'data': [
        'data/hr_work_entry_type_data.xml',
        # 'views/resource_calendar_leaves_views.xml',
    ],
    "maintainers": ["nimarosa"],
    "installable": True,
    "application": True,
    "auto_install": True,
}