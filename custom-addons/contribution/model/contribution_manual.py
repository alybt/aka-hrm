from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    x_employee_sss_number = fields.Char(
        string="SSS Number",
        related='employee_id.x_employee_sss_number',
        readonly=True,
        store=True
    )

    x_employee_philhealth_number = fields.Char(
        string="PhilHealth Number",
        related='employee_id.x_employee_philhealth_number',
        readonly=True,
        store=True
    )

    x_employee_pagibig_number = fields.Char(
        string="Pag-IBIG Number",
        related='employee_id.x_employee_pagibig_number',
        readonly=True,
        store=True
    )

    x_employee_is_active = fields.Boolean(
        string="Active Contribution",
        related='employee_id.x_employee_is_active',
        readonly=True,
        store=True
    )

    x_sss_contribution = fields.Float(string="SSS Contribution Amount")
    x_philhealth_contribution = fields.Float(string="PhilHealth Contribution Amount")
    x_pagibig_contribution = fields.Float(string="Pag-IBIG Contribution Amount")