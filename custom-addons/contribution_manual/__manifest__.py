{
    'name': 'PH Payroll Manual Contribution Overrides',
    'version': '1.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Manually override SSS, PhilHealth, and Pag-IBIG rates',
    'depends': ['payroll', 'hr_contract', 'hr'],
    'data': [
        'views/hr_contract_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}