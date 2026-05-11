from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    # Add the Many2many field and computed total
    hr_expense_ids = fields.Many2many(
        'hr.expense', 
        string='Linked Expenses',
        help='Expenses reimbursed through this payslip'
    )
    
    x_reimbursement_total = fields.Float(
        string='Total Reimbursement',
        compute='_compute_reimbursement_total',
        store=True,
        help='Total amount of all expenses linked to this payslip'
    )
    
    x_auto_link_expenses = fields.Boolean(
        string='Auto Link Expenses',
        default=True,
        help='Automatically link approved expenses to payslip'
    )
    
    @api.depends('hr_expense_ids', 'hr_expense_ids.total_amount')
    def _compute_reimbursement_total(self):
        """Compute total reimbursement from linked expenses"""
        for payslip in self:
            total = 0.0
            for expense in payslip.hr_expense_ids:
                total += expense.total_amount
                _logger.info(f"Expense {expense.id}: Amount {expense.total_amount}")
            
            payslip.x_reimbursement_total = total
            _logger.info(f"Payslip {payslip.id}: Total Reimbursement = {total}")
    
    def _auto_link_expenses(self):
        """Automatically link approved expenses to payslip"""
        for payslip in self:
            if not payslip.x_auto_link_expenses:
                continue
            
            _logger.info(f"Auto-linking expenses for payslip {payslip.name}")
                
            # Search for approved expenses for this employee
            approved_expenses = self.env['hr.expense'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'approved'),
                ('date', '>=', payslip.date_from),
                ('date', '<=', payslip.date_to),
                ('x_payslip_id', '=', False),
                ('x_report_in_payslip', '=', True)  # Only get expenses marked for payslip
            ])
            
            # Also get older approved expenses not yet paid
            older_expenses = self.env['hr.expense'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('state', '=', 'approved'),
                ('date', '<', payslip.date_from),
                ('x_payslip_id', '=', False),
                ('x_report_in_payslip', '=', True)
            ])
            
            # Combine both searches
            all_expenses = approved_expenses | older_expenses
            
            if all_expenses:
                _logger.info(f"Found {len(all_expenses)} expenses to link")
                
                # Add to existing expenses (avoid duplicates)
                existing_ids = payslip.hr_expense_ids.ids
                new_ids = all_expenses.ids
                combined_ids = list(set(existing_ids + new_ids))
                
                payslip.hr_expense_ids = [(6, 0, combined_ids)]
                _logger.info(f"Auto-linked {len(all_expenses)} expenses to payslip {payslip.name}")
                
                # Store which payslip these expenses are linked to
                for expense in all_expenses:
                    expense.write({'x_payslip_id': payslip.id})
    
    def action_payslip_done(self):
        """Mark linked expenses as paid when payslip is confirmed"""
        _logger.info("=== Starting action_payslip_done ===")
        
        # Auto-link expenses before confirming
        self._auto_link_expenses()
        
        # Call parent method
        res = super().action_payslip_done()
        
        # Update expense states AFTER parent method completes
        for payslip in self:
            if payslip.hr_expense_ids:
                _logger.info(f"Processing {len(payslip.hr_expense_ids)} expenses for payslip {payslip.name}")
                
                for expense in payslip.hr_expense_ids:
                    _logger.info(f"Expense {expense.id}: Current state = {expense.state}")
                    
                    # Method 1: Try direct write
                    if expense.state == 'approved':
                        try:
                            # Use sudo to bypass security restrictions
                            expense.sudo().write({'state': 'done'})
                            _logger.info(f"Successfully marked expense {expense.id} as done")
                        except Exception as e:
                            _logger.error(f"Error marking expense {expense.id}: {e}")
                            
                            # Method 2: Use button action if write fails
                            try:
                                if hasattr(expense, 'action_submit_expenses'):
                                    expense.action_submit_expenses()
                                expense.sudo().action_move_create()
                                _logger.info(f"Used alternative method for expense {expense.id}")
                            except Exception as e2:
                                _logger.error(f"Alternative method also failed: {e2}")
                
                # Verify the changes
                for expense in payslip.hr_expense_ids:
                    _logger.info(f"Expense {expense.id} final state: {expense.state}")
                
        return res
    
    def action_payslip_cancel(self):
        """Reset expenses to approved when payslip is cancelled"""
        _logger.info("=== Starting action_payslip_cancel ===")
        
        res = super().action_payslip_cancel()
        
        for payslip in self:
            if payslip.hr_expense_ids:
                for expense in payslip.hr_expense_ids:
                    if expense.state == 'done':
                        try:
                            expense.sudo().write({'state': 'approved'})
                            expense.sudo().write({'x_payslip_id': False})
                            _logger.info(f"Reset expense {expense.id} to approved")
                        except Exception as e:
                            _logger.error(f"Error resetting expense {expense.id}: {e}")
                
        return res

    @api.constrains('hr_expense_ids')
    def _check_unique_expenses(self):
        """Prevent expenses from being linked to multiple payslips"""
        for payslip in self:
            for expense in payslip.hr_expense_ids:
                # Skip if this is the same payslip
                existing_payslips = self.search([
                    ('id', '!=', payslip.id),
                    ('hr_expense_ids', 'in', expense.id),
                    ('state', 'not in', ['cancel', 'draft'])
                ])
                if existing_payslips:
                    raise ValidationError(
                        f"Expense {expense.name} is already linked to payslip {existing_payslips[0].name}!"
                    )

    @api.model
    def create(self, vals):
        """Auto-link approved expenses when creating payslip"""
        payslip = super().create(vals)
        payslip._auto_link_expenses()
        return payslip

    def write(self, vals):
        """Trigger auto-link when payslip is computed or state changes"""
        result = super().write(vals)
        
        if 'state' in vals and vals['state'] in ['draft', 'verify']:
            for payslip in self:
                payslip._auto_link_expenses()
        
        if 'hr_expense_ids' in vals:
            for payslip in self:
                payslip._compute_reimbursement_total()
                
        return result
    
    def action_refresh_expenses(self):
        """Manual button to refresh and link expenses"""
        self._auto_link_expenses()
        self._compute_reimbursement_total()
        
        linked_count = len(self.hr_expense_ids)
        expense_states = [exp.state for exp in self.hr_expense_ids]
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Expenses Updated',
                'message': f'Linked {linked_count} expenses. States: {expense_states}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def compute_sheet(self):
        """Override compute_sheet to ensure expenses are linked before computation"""
        self._auto_link_expenses()
        return super().compute_sheet()
    
    def action_force_pay_expenses(self):
        """Manual button to force mark expenses as paid"""
        self.ensure_one()
        
        if not self.hr_expense_ids:
            raise UserError("No expenses linked to this payslip!")
        
        for expense in self.hr_expense_ids:
            if expense.state == 'approved':
                expense.sudo().write({'state': 'done'})
                _logger.info(f"Force marked expense {expense.id} as done")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Marked {len(self.hr_expense_ids)} expenses as paid',
                'type': 'success',
            }
        }


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    x_payslip_id = fields.Many2one(
        'hr.payslip',
        string='Linked Payslip',
        help='Payslip that this expense is reimbursed through'
    )
    
    x_report_in_payslip = fields.Boolean(
        string='Report in Payslip',
        default=True,
        help='If checked, this expense will be automatically included in the next payslip'
    )
    
    def action_approve_expenses(self):
        """Override to add logging"""
        res = super().action_approve_expenses()
        _logger.info(f"Expenses approved: {self.ids}")
        return res