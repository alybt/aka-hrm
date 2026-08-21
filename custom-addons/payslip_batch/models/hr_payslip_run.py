from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_batch_compute(self):
        """Compute all payslips in this batch"""
        self.ensure_one()

        payslips = self.slip_ids.filtered(lambda p: p.state in ['draft', 'verify'])

        if not payslips:
            raise UserError(_("No computable payslips found in this batch."))

        computed = 0
        errors = []

        for payslip in payslips:
            try:
                payslip.compute_sheet()
                computed += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) computed successfully.") % (self.name, computed)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_batch_confirm(self):
        """Confirm all verified payslips in this batch (Verify -> Done)"""
        self.ensure_one()

        # Only verify state payslips can be confirmed to done state
        payslips = self.slip_ids.filtered(lambda p: p.state == 'verify')

        if not payslips:
            raise UserError(_("No verified payslips found to confirm in this batch."))

        confirmed = 0
        errors = []

        for payslip in payslips:
            try:
                # Move from verify to done
                payslip.action_payslip_done()  # This moves from verify to done
                confirmed += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) moved to Done state successfully.") % (self.name, confirmed)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_batch_done(self):
        """Mark all verified payslips as done in this batch (Verify -> Done)"""
        self.ensure_one()

        # Only verify state payslips can be marked as done
        payslips = self.slip_ids.filtered(lambda p: p.state == 'verify')

        if not payslips:
            raise UserError(_("No verified payslips found to mark as done in this batch."))

        done_count = 0
        errors = []

        for payslip in payslips:
            try:
                payslip.action_payslip_done()  # This moves from verify to done
                done_count += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) marked as Done successfully.") % (self.name, done_count)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_batch_cancel(self):
        """Cancel all eligible payslips in this batch"""
        self.ensure_one()

        # Exclude already paid payslips
        payslips = self.slip_ids.filtered(
            lambda p: p.state in ['draft', 'verify', 'done'] and not p.paid
        )

        if not payslips:
            raise UserError(_("No cancellable payslips found in this batch."))

        cancelled = 0
        errors = []

        for payslip in payslips:
            try:
                payslip.action_payslip_cancel()
                cancelled += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) cancelled successfully.") % (self.name, cancelled)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_batch_set_to_draft(self):
        """Set all cancelled payslips to draft in this batch"""
        self.ensure_one()

        payslips = self.slip_ids.filtered(lambda p: p.state == 'cancel')

        if not payslips:
            raise UserError(_("No cancelled payslips found in this batch."))

        drafted = 0
        errors = []

        for payslip in payslips:
            try:
                payslip.action_payslip_draft()
                drafted += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) set to draft successfully.") % (self.name, drafted)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_batch_refetch(self):
        """Refetch data for all draft payslips in this batch"""
        self.ensure_one()

        payslips = self.slip_ids.filtered(lambda p: p.state == 'draft')

        if not payslips:
            raise UserError(_("No draft payslips found to refetch data in this batch."))

        refetched = 0
        errors = []

        for payslip in payslips:
            try:
                # Refresh employee and contract data for Odoo 17
                if hasattr(payslip, '_onchange_employee_id'):
                    payslip._onchange_employee_id()
                if hasattr(payslip, '_compute_worked_days'):
                    payslip._compute_worked_days()
                if hasattr(payslip, '_compute_lines'):
                    payslip._compute_lines()
                # For Odoo 17, also refresh input lines
                if hasattr(payslip, '_compute_input_line_ids'):
                    payslip._compute_input_line_ids()
                refetched += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) data refetched successfully.") % (self.name, refetched)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)
            return self._show_notification(message, 'warning')

        return self._show_notification(message, 'success')

    def action_validate_all(self):
        """Complete validation: Compute -> Verify -> Done for all payslips in batch"""
        self.ensure_one()

        unconfirmed_payslips = self.slip_ids.filtered(lambda p: p.state != 'done')

        if unconfirmed_payslips:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'confirm.batch.validation.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_batch_id': self.id,
                    'default_payslip_count': len(unconfirmed_payslips),
                }
            }
        else:
            raise UserError(_("All payslips in this batch are already confirmed."))

    def _show_notification(self, message, type='info'):
        """Show notification message for Odoo 17"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Batch Operation Result"),
                'message': message,
                'type': type,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class ConfirmBatchValidationWizard(models.TransientModel):
    _name = 'confirm.batch.validation.wizard'
    _description = 'Confirm Batch Validation Wizard'

    batch_id = fields.Many2one('hr.payslip.run', string='Payslip Batch', required=True)
    payslip_count = fields.Integer(string='Number of Payslips', readonly=True)

    def action_confirm_validate(self):
        """Complete validation: Compute -> Verify -> Done for all payslips"""
        self.ensure_one()

        payslips = self.batch_id.slip_ids.filtered(lambda p: p.state != 'done')

        validated = 0
        errors = []

        for payslip in payslips:
            try:
                # Step 1: Compute if not computed
                if payslip.state == 'draft':
                    payslip.compute_sheet()

                # Step 2: Move from draft to verify if needed
                if payslip.state == 'draft':
                    payslip.action_payslip_verify()

                # Step 3: Move from verify to done
                if payslip.state == 'verify':
                    payslip.action_payslip_done()

                validated += 1
            except Exception as e:
                errors.append(_("%s: %s") % (payslip.name, str(e)))

        message = _("Batch '%s': %d payslip(s) fully validated (Done) successfully.") % (self.batch_id.name, validated)
        if errors:
            message += _("\n\nErrors:\n%s") % "\n".join(errors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Batch Validation Result"),
                'message': message,
                'type': 'success' if not errors else 'warning',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }