{
    "name": "Payslip Batch Summary",
    "version": "17.0.1.0.0",
    "category": "Human Resources/Payroll",
    "summary": "Generate a detailed summary report for a payslip batch",
    "depends": ["payroll", "hr_contract", "base"],
    "data": [
        "security/ir.model.access.xml",
        "views/report_payslip_batch_summary.xml",
        "views/wizard_view.xml",
        "views/payslip_run_view_inherit.xml",
    ],
    "installable": True,
    "application": False,
}
