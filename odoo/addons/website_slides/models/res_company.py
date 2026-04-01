from odoo import models, api
from odoo.tools import config

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _set_google_key_from_config(self): 
        key = config.get('google_app_key')
        if key:
            self.env.company.write({'website_slide_google_app_key': key})