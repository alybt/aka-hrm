# Copyright (C) 2021 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Payroll Public Holidays",
    "version": "17.0.1.0.0",
    "category": "Payroll",
    "website": "https://github.com/OCA/payroll",
    "summary": "Integration between payroll and hr_public_holidays",
    "license": "AGPL-3",
    "author": "Nimarosa, Odoo Community Association (OCA)",
    "depends": ["payroll", 
                "hr_holidays", 
                "hr_holidays_public",
                "hr_work_entry",
                ],
    "data": [],
    "installable": True,
    "maintainers": ["nimarosa"],
    "installable": True,
    "application": True,
    "auto_install": True,
}
