{
    "name": "Batch Payslip Print",
    "version": "17.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Print all payslips in a batch using custom layout",
    "description": """
        Adds a "Print All Payslips" button to Payslip Batch forms.
        Generates a single PDF with one payslip per employee, using your custom payslip report.
    """,
    "depends": ["payroll", "payslip_report"],
    "data": [
        "reports/batch_payslip_report.xml",
        "views/hr_payslip_run_views.xml",
    ],
    "installable": True,
    "application": False,
}
