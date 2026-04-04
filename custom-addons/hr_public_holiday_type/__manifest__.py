# -*- coding: utf-8 -*-
{
    'name': 'Public Holiday Type',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Add holiday type classification to Public Holidays',
    'description': """
Public Holiday Type
===================
This module adds a **Holiday Type** field to the Public Holidays configuration,
allowing HR to classify each holiday as one of the following:

* **Regular Holiday** - National rest days with full pay (e.g. New Year's Day, Christmas)
* **Special Non-Working Day** - No work required; pay depends on company policy
* **Special Working Day** - Declared working days that fall on a holiday
* **Local Holiday** - City- or province-declared holidays

The classification appears on:
- The Public Holidays list and form views
- The Leave Allocation / Time Off reports (optional)
    """,
    'author': 'Custom Development',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/resource_calendar_leaves_views.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
}
