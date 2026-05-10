from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class PHEmployeeIDs(models.Model):
    _name = 'ph.employee.ids'
    _description = 'Philippine Employee Government IDs'
    _rec_name = 'employee_id'
    _order = 'employee_id, is_active DESC'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True,
        ondelete='cascade'
    )

    # Government IDs
    sss_number = fields.Char(
        string="SSS Number",
        help="Format: XX-XXXXXXX-X (10 digits total)\nExample: 34-1234567-8"
    )

    philhealth_number = fields.Char(
        string="PhilHealth Number",
        help="Format: XX-XXXXXXXXX-X (12 digits total)\nExample: 12-012345678-9"
    )

    pagibig_number = fields.Char(
        string="Pag-IBIG Number",
        help="Format: XXXX-XXXX-XXXX (12 digits total)\nExample: 1212-3456-7890"
    )

    tin_number = fields.Char(
        string="TIN Number",
        help="Format: XXX-XXX-XXX-XXX (12 digits total)\nExample: 123-456-789-000"
    )

    # Status
    is_active = fields.Boolean(
        string="Current ID / Active Contribution",
        default=True,
        help="Check if these IDs are currently active for contributions"
    )

    # Additional status fields for clarity
    active_status = fields.Selection(
        [
            ('active', 'Active - Currently Contributing'),
            ('inactive', 'Inactive - Historical Record'),
            ('pending', 'Pending - Awaiting Verification'),
        ],
        string="Contribution Status",
        default='active',
        compute='_compute_active_status',
        store=True
    )

    activation_date = fields.Date(
        string="Activation Date",
        default=fields.Date.today,
        help="Date when this ID became active"
    )

    deactivation_date = fields.Date(
        string="Deactivation Date",
        help="Date when this ID was deactivated"
    )

    notes = fields.Text(string="Notes")

    # Company context
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        readonly=True
    )

    @api.depends('is_active')
    def _compute_active_status(self):
        for record in self:
            if record.is_active:
                record.active_status = 'active'
            else:
                record.active_status = 'inactive'

    @api.constrains('is_active', 'employee_id')
    def _check_unique_active(self):
        """Ensure only one active ID record per employee"""
        for record in self:
            if record.is_active:
                # Find other active records for same employee
                other_active = self.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('is_active', '=', True),
                    ('id', '!=', record.id)
                ])
                if other_active:
                    raise ValidationError(
                        f"Employee {record.employee_id.name} already has an active ID record.\n"
                        f"Please deactivate the existing record first: "
                        f"SSS: {other_active[0].sss_number or 'N/A'}, "
                        f"TIN: {other_active[0].tin_number or 'N/A'}"
                    )

    @api.constrains('sss_number')
    def _validate_sss_number(self):
        for record in self:
            if record.sss_number:
                digits = re.sub(r'\D', '', record.sss_number)
                if len(digits) != 10:
                    raise ValidationError(
                        "SSS Number must contain exactly 10 digits.\n"
                        "Format: XX-XXXXXXX-X (Example: 34-1234567-8)"
                    )
                if not re.match(r'^\d{2}-\d{7}-\d{1}$', record.sss_number):
                    raise ValidationError(
                        "SSS Number must follow format: XX-XXXXXXX-X\n"
                        "Example: 34-1234567-8"
                    )

    @api.constrains('philhealth_number')
    def _validate_philhealth_number(self):
        for record in self:
            if record.philhealth_number:
                digits = re.sub(r'\D', '', record.philhealth_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "PhilHealth Number must contain exactly 12 digits.\n"
                        "Format: XX-XXXXXXXXX-X (Example: 12-012345678-9)"
                    )
                if not re.match(r'^\d{2}-\d{9}-\d{1}$', record.philhealth_number):
                    raise ValidationError(
                        "PhilHealth Number must follow format: XX-XXXXXXXXX-X\n"
                        "Example: 12-012345678-9"
                    )

    @api.constrains('pagibig_number')
    def _validate_pagibig_number(self):
        for record in self:
            if record.pagibig_number:
                digits = re.sub(r'\D', '', record.pagibig_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "Pag-IBIG Number must contain exactly 12 digits.\n"
                        "Format: XXXX-XXXX-XXXX (Example: 1212-3456-7890)"
                    )
                if not re.match(r'^\d{4}-\d{4}-\d{4}$', record.pagibig_number):
                    raise ValidationError(
                        "Pag-IBIG Number must follow format: XXXX-XXXX-XXXX\n"
                        "Example: 1212-3456-7890"
                    )

    @api.constrains('tin_number')
    def _validate_tin_number(self):
        for record in self:
            if record.tin_number:
                digits = re.sub(r'\D', '', record.tin_number)
                if len(digits) != 12:
                    raise ValidationError(
                        "TIN Number must contain exactly 12 digits.\n"
                        "Format: XXX-XXX-XXX-XXX (Example: 123-456-789-000)"
                    )
                if not re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', record.tin_number):
                    raise ValidationError(
                        "TIN Number must follow format: XXX-XXX-XXX-XXX\n"
                        "Example: 123-456-789-000"
                    )

    @api.model
    def create(self, vals):
        # Auto-format numbers before creating
        if 'sss_number' in vals:
            vals['sss_number'] = self._format_sss(vals['sss_number'])
        if 'philhealth_number' in vals:
            vals['philhealth_number'] = self._format_philhealth(vals['philhealth_number'])
        if 'pagibig_number' in vals:
            vals['pagibig_number'] = self._format_pagibig(vals['pagibig_number'])
        if 'tin_number' in vals:
            vals['tin_number'] = self._format_tin(vals['tin_number'])

        # If this is being set as active, deactivate others first
        if vals.get('is_active'):
            employee_id = vals.get('employee_id')
            if employee_id:
                other_active = self.search([
                    ('employee_id', '=', employee_id),
                    ('is_active', '=', True)
                ])
                if other_active:
                    other_active.write({'is_active': False})

        return super().create(vals)

    def write(self, vals):
        # Auto-format numbers before writing
        if 'sss_number' in vals:
            vals['sss_number'] = self._format_sss(vals['sss_number'])
        if 'philhealth_number' in vals:
            vals['philhealth_number'] = self._format_philhealth(vals['philhealth_number'])
        if 'pagibig_number' in vals:
            vals['pagibig_number'] = self._format_pagibig(vals['pagibig_number'])
        if 'tin_number' in vals:
            vals['tin_number'] = self._format_tin(vals['tin_number'])

        # Handle activation/deactivation dates
        if 'is_active' in vals:
            for record in self:
                if vals['is_active'] and not record.is_active:
                    # Activating: set activation date
                    vals['activation_date'] = fields.Date.today()
                    # Deactivate other records for this employee
                    other_active = self.search([
                        ('employee_id', '=', record.employee_id.id),
                        ('is_active', '=', True),
                        ('id', '!=', record.id)
                    ])
                    if other_active:
                        other_active.write({'is_active': False, 'deactivation_date': fields.Date.today()})
                elif not vals['is_active'] and record.is_active:
                    # Deactivating: set deactivation date
                    vals['deactivation_date'] = fields.Date.today()

        return super().write(vals)

    def action_activate(self):
        """Button action to activate this ID record"""
        for record in self:
            # Deactivate all other active records for this employee
            other_active = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('is_active', '=', True),
                ('id', '!=', record.id)
            ])
            if other_active:
                other_active.write({
                    'is_active': False,
                    'deactivation_date': fields.Date.today()
                })
            # Activate this record
            record.write({
                'is_active': True,
                'activation_date': fields.Date.today(),
                'deactivation_date': False
            })

    def action_deactivate(self):
        """Button action to deactivate this ID record"""
        for record in self:
            record.write({
                'is_active': False,
                'deactivation_date': fields.Date.today()
            })

    def _format_sss(self, value):
        """Format SSS: XX-XXXXXXX-X"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 10:
            return f"{digits[:2]}-{digits[2:9]}-{digits[9:10]}"
        return value

    def _format_philhealth(self, value):
        """Format PhilHealth: XX-XXXXXXXXX-X"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:2]}-{digits[2:11]}-{digits[11:12]}"
        return value

    def _format_pagibig(self, value):
        """Format Pag-IBIG: XXXX-XXXX-XXXX"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}"
        return value

    def _format_tin(self, value):
        """Format TIN: XXX-XXX-XXX-XXX"""
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) >= 12:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:9]}-{digits[9:12]}"
        return value