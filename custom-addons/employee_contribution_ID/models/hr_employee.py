from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ph_government_ids = fields.One2many(
        'ph.employee.ids',
        'employee_id',
        string="Philippine Government IDs"
    )

    x_employee_tin_number = fields.Char(
        string="TIN Number",
        related='ph_government_ids.tin_number',
        readonly=False,
        store=True
    )

    x_employee_sss_number = fields.Char(
        string="SSS Number",
        related='ph_government_ids.sss_number',
        readonly=False,
        store=True
    )

    x_employee_philhealth_number = fields.Char(
        string="PhilHealth Number",
        related='ph_government_ids.philhealth_number',
        readonly=False,
        store=True
    )

    x_employee_pagibig_number = fields.Char(
        string="Pag-IBIG Number",
        related='ph_government_ids.pagibig_number',
        readonly=False,
        store=True
    )

    x_employee_is_active = fields.Boolean(
        string="Active Contribution",
        related='ph_government_ids.is_active',
        readonly=False,
        store=True,
        help="Check if these IDs are currently active for government contributions"
    )

    # Validation constraints
    @api.constrains('x_employee_tin_number')
    def _validate_tin_number(self):
        for record in self:
            if record.x_employee_tin_number:
                # Remove non-digits for validation
                digits = re.sub(r'\D', '', record.x_employee_tin_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "TIN Number must contain exactly 12 digits.\n"
                        "Format: XXX-XXX-XXX-XXX (Example: 123-456-789-000)"
                    )
                # Check format with hyphens
                if not re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', record.x_employee_tin_number):
                    raise ValidationError(
                        "TIN Number must follow format: XXX-XXX-XXX-XXX\n"
                        "Example: 123-456-789-000"
                    )

    @api.constrains('x_employee_sss_number')
    def _validate_sss_number(self):
        for record in self:
            if record.x_employee_sss_number:
                digits = re.sub(r'\D', '', record.x_employee_sss_number)
                if len(digits) != 10:
                    raise ValidationError(
                        "SSS Number must contain exactly 10 digits.\n"
                        "Format: XX-XXXXXXX-X (Example: 34-1234567-8)"
                    )
                if not re.match(r'^\d{2}-\d{7}-\d{1}$', record.x_employee_sss_number):
                    raise ValidationError(
                        "SSS Number must follow format: XX-XXXXXXX-X\n"
                        "Example: 34-1234567-8"
                    )

    @api.constrains('x_employee_philhealth_number')
    def _validate_philhealth_number(self):
        for record in self:
            if record.x_employee_philhealth_number:
                digits = re.sub(r'\D', '', record.x_employee_philhealth_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "PhilHealth Number must contain exactly 12 digits.\n"
                        "Format: XX-XXXXXXXXX-X (Example: 12-012345678-9)"
                    )
                if not re.match(r'^\d{2}-\d{9}-\d{1}$', record.x_employee_philhealth_number):
                    raise ValidationError(
                        "PhilHealth Number must follow format: XX-XXXXXXXXX-X\n"
                        "Example: 12-012345678-9"
                    )

    @api.constrains('x_employee_pagibig_number')
    def _validate_pagibig_number(self):
        for record in self:
            if record.x_employee_pagibig_number:
                digits = re.sub(r'\D', '', record.x_employee_pagibig_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "Pag-IBIG Number must contain exactly 12 digits.\n"
                        "Format: XXXX-XXXX-XXXX (Example: 1212-3456-7890)"
                    )
                if not re.match(r'^\d{4}-\d{4}-\d{4}$', record.x_employee_pagibig_number):
                    raise ValidationError(
                        "Pag-IBIG Number must follow format: XXXX-XXXX-XXXX\n"
                        "Example: 1212-3456-7890"
                    )

    # Optional: Auto-format before saving
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'x_employee_tin_number' in vals:
                vals['x_employee_tin_number'] = self._auto_format_tin(vals['x_employee_tin_number'])
            if 'x_employee_sss_number' in vals:
                vals['x_employee_sss_number'] = self._auto_format_sss(vals['x_employee_sss_number'])
            if 'x_employee_philhealth_number' in vals:
                vals['x_employee_philhealth_number'] = self._auto_format_philhealth(vals['x_employee_philhealth_number'])
            if 'x_employee_pagibig_number' in vals:
                vals['x_employee_pagibig_number'] = self._auto_format_pagibig(vals['x_employee_pagibig_number'])
        return super().create(vals_list)

    def write(self, vals):
        if 'x_employee_tin_number' in vals:
            vals['x_employee_tin_number'] = self._auto_format_tin(vals['x_employee_tin_number'])
        if 'x_employee_sss_number' in vals:
            vals['x_employee_sss_number'] = self._auto_format_sss(vals['x_employee_sss_number'])
        if 'x_employee_philhealth_number' in vals:
            vals['x_employee_philhealth_number'] = self._auto_format_philhealth(vals['x_employee_philhealth_number'])
        if 'x_employee_pagibig_number' in vals:
            vals['x_employee_pagibig_number'] = self._auto_format_pagibig(vals['x_employee_pagibig_number'])
        return super().write(vals)

    def _auto_format_tin(self, value):
        """Auto-format TIN: 123-456-789-000"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}"
        return value

    def _auto_format_sss(self, value):
        """Auto-format SSS: 34-1234567-8"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 10:
            return f"{digits[:2]}-{digits[2:9]}-{digits[9:10]}"
        return value

    def _auto_format_philhealth(self, value):
        """Auto-format PhilHealth: 12-012345678-9"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:2]}-{digits[2:11]}-{digits[11:12]}"
        return value

    def _auto_format_pagibig(self, value):
        """Auto-format Pag-IBIG: 1212-3456-7890"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}"
        return value