{
    'name': 'HR Absence Counter with Payslip Integration',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Count employee absences excluding holidays with payslip integration',
    'description': """
        This module counts employee absences from work schedule
        while excluding configured holiday types from being counted as absences.
        
        Features:
        - Excludes holidays from absence counting
        - Integrates with payslip computation
        - Automatically deducts absences from salary
        - Shows detailed absence breakdown in payslip
        
        Holiday Types excluded:
        - Regular Holiday
        - Special Non-Working Holiday  
        - Special Working Holiday
        - Local Holiday
    """,
    'author': 'AKA',
    'website': '',
    'depends': ['hr', 'hr_holidays', 'hr_attendance', 'hr_payroll', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rule_data.xml',
        'views/hr_employee_views.xml',
        'views/hr_absence_count_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_contract_views.xml',
        'data/absence_count_cron.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'LGPL-3',
}