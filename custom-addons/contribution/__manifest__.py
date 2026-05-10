{
    'name': 'PH Contribution Manual',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Has Company and, Employe Details for Contribution ID and you can manually setup the Contribution for each Employee ',
    'depends': ['payroll', 'hr_contract', 'hr'],
    'data': [
        'views/compnay_ID.xml',
        'views/hr_payslip_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": True,
    'license': 'LGPL-3',
}