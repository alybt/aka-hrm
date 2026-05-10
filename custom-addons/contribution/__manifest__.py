{
    'name': 'PH Contribution Manual',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Has Company and, Employe Details for Contribution ID and you can manually setup the Contribution for each Employee ',
    'depends': ['payroll', 'hr_contract', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_contribtion_ID.xml',
        'views/employee_ID.xml',
        'views/company_ID.xml',
        'views/contribution_manual.xml',
        'views/payslip_display.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    'license': 'LGPL-3',
}