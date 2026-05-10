# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Payroll Contract Advantages",
    "version": "17.0.1.0.0",
    "category": "Payroll",
    "website": "https://github.com/OCA/payroll",
    "summary": "Allow to define contract advantages for employees.",
    "license": "LGPL-3",
    "author": "Nimarosa, Odoo Community Association (OCA)",
    "depends": ["hr_contract", 
                "payroll",
                "hr_work_entry",
                ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_contract_advantage_views.xml",
        "views/hr_contract_views.xml",
    ], 
    "maintainers": ["nimarosa"],
    "installable": True,
    "application": True,
    "auto_install": True,
}
