from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class ResCompany(models.Model):
    _inherit = 'res.company'

    sss_employer_id = fields.Char(string="SSS Employer Number")
    tin_id = fields.Char(string="TIN Number")
    philhealth_employer_id = fields.Char(string="PhilHealth Employer Number")
    pagibig_employer_id = fields.Char(string="Pag-IBIG Employer Number")

    @api.constrains('sss_employer_id', 'tin_id', 'philhealth_employer_id', 'pagibig_employer_id')
    def _validate_ids(self):
        for record in self:
            if record.sss_employer_id:
                digits = re.sub(r'\D', '', record.sss_employer_id)
                if len(digits) != 14:
                    raise ValidationError("SSS Employer must contain exactly 14 digits (Format: 03-9876543-2-000)")

            if record.tin_id:
                digits = re.sub(r'\D', '', record.tin_id)
                if len(digits) != 12:
                    raise ValidationError("TIN must contain exactly 12 digits (Format: 123-456-789-000)")

            if record.philhealth_employer_id:
                digits = re.sub(r'\D', '', record.philhealth_employer_id)
                if len(digits) != 12:
                    raise ValidationError("PhilHealth must contain exactly 12 digits (Format: 02-123456789-0)")

            if record.pagibig_employer_id:
                digits = re.sub(r'\D', '', record.pagibig_employer_id)
                if len(digits) != 12:
                    raise ValidationError("Pag-IBIG must contain exactly 12 digits (Format: 1212-3456-7890)")