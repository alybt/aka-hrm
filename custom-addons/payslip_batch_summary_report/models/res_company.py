from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    x_single_line_address = fields.Char(
        string="Single Line Address",
        compute='_compute_single_line_address'
    )

    @api.depends('partner_id.street', 'partner_id.street2', 'partner_id.city', 'partner_id.state_id')
    def _compute_single_line_address(self):
        for company in self:
            parts = []
            if company.partner_id.street:
                parts.append(company.partner_id.street)
            if company.partner_id.street2:
                parts.append(company.partner_id.street2)
            if company.partner_id.city:
                parts.append(company.partner_id.city)
            if company.partner_id.state_id:
                parts.append(company.partner_id.state_id.name)

            company.x_single_line_address = ", ".join(parts) if parts else ""