from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    x_holiday_regular = fields.Float(string="Regular Holidays", compute="_compute_holiday_counts", store=True)
    x_holiday_special_nw = fields.Float(string="Special Non-Working", compute="_compute_holiday_counts", store=True)
    x_holiday_special_w = fields.Float(string="Special Working", compute="_compute_holiday_counts", store=True)
    x_holiday_local = fields.Float(string="Local Holidays", compute="_compute_holiday_counts", store=True)

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_holiday_counts(self):
        for slip in self: 
            reg = snw = sw = loc = 0
            
            if slip.date_from and slip.date_to and slip.employee_id.resource_calendar_id: 
                holidays = self.env['resource.calendar.leaves'].search([
                    ('calendar_id', '=', slip.employee_id.resource_calendar_id.id),
                    ('date_from', '<=', fields.Datetime.to_string(slip.date_to)),
                    ('date_to', '>=', fields.Datetime.to_string(slip.date_from)),
                ])

                for holiday in holidays: 
                    if holiday.x_holiday_types == 'regular':
                        reg += 1
                    elif holiday.x_holiday_types == 'special_non_working':
                        snw += 1
                    elif holiday.x_holiday_types == 'special_working':
                        sw += 1
                    elif holiday.x_holiday_types == 'local':
                        loc += 1

            slip.x_holiday_regular = reg
            slip.x_holiday_special_nw = snw
            slip.x_holiday_special_w = sw
            slip.x_holiday_local = loc