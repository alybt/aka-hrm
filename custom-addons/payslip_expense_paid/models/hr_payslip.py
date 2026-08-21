import logging

from odoo.exceptions import UserError

from odoo import _, models

_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_done(self):
        """
        Override to mark linked expense sheets as paid when payslip is confirmed.
        Bypasses the Register Payment popup by directly setting state/payment_state.
        """
        # First, call the parent to confirm the payslip
        res = super().action_payslip_done()

        # Now, for each payslip, update its linked expense sheets
        for payslip in self:
            if payslip.hr_expense_ids:
                _logger.info("Processing expense sheets for payslip %s", payslip.name)

                # Get all expense sheets linked to these expenses
                expense_sheets = payslip.hr_expense_ids.mapped("sheet_id")
                # Only update sheets that are not yet paid
                expense_sheets = expense_sheets.filtered(
                    lambda s: s.state in ("approve", "approved", "post") and s.payment_state != "paid"
                )

                if expense_sheets:
                    _logger.info(
                        "Found %s expense sheets to mark as paid", len(expense_sheets)
                    )

                    for sheet in expense_sheets:
                        try:
                            # Bypass the Register Payment popup – directly set the fields
                            sheet.sudo().write(
                                {
                                    "payment_state": "paid",
                                    "state": "done",  # or 'post' if you prefer
                                }
                            )
                            _logger.info(
                                "Sheet %s marked as paid via direct write", sheet.id
                            )

                            # Update individual expenses to 'done' as well
                            expenses = sheet.expense_line_ids
                            for expense in expenses.filtered(
                                lambda e: e.state in ("approved", "approve", "reported")
                            ):
                                expense.sudo().write({"state": "done"})
                                _logger.info("Expense %s marked as done", expense.id)

                        except Exception as e:
                            _logger.error(
                                "Failed to mark sheet %s as paid: %s", sheet.id, e
                            )
                            continue

                    _logger.info(
                        "Updated %s expense sheets for payslip %s",
                        len(expense_sheets),
                        payslip.name,
                    )

        return res

    def action_payslip_cancel(self):
        """
        When payslip is cancelled, reset linked expense sheets back to 'approved' / 'not_paid'
        """
        res = super().action_payslip_cancel()

        for payslip in self:
            if payslip.hr_expense_ids:
                # Get sheets linked to this payslip
                expense_sheets = payslip.hr_expense_ids.mapped("sheet_id")
                expense_sheets = expense_sheets.filtered(
                    lambda s: s.payment_state == "paid" or s.state == "done"
                )

                for sheet in expense_sheets:
                    try:
                        # Revert the sheet
                        sheet.sudo().write(
                            {
                                "payment_state": "not_paid",
                                "state": "approve", # Odoo standard state for approved is 'approve'
                            }
                        )
                        _logger.info("Sheet %s reverted to approved/not_paid", sheet.id)

                        # Also revert individual expenses
                        expenses = sheet.expense_line_ids
                        for expense in expenses.filtered(lambda e: e.state == "done"):
                            expense.sudo().write({"state": "approved"}) # hr.expense uses 'approved'
                            _logger.info("Expense %s reverted to approved", expense.id)

                    except Exception as e:
                        _logger.error("Failed to revert sheet %s: %s", sheet.id, e)

        return res

    def action_force_pay_linked_expenses(self):
        """
        Manual button to force-mark linked expense sheets as paid.
        (Same logic – no popup)
        """
        self.ensure_one()
        if not self.hr_expense_ids:
            raise UserError(_("No expenses linked to this payslip."))

        expense_sheets = self.hr_expense_ids.mapped("sheet_id")
        expense_sheets = expense_sheets.filtered(
            lambda s: s.payment_state != "paid" and s.state != "done"
        )

        if not expense_sheets:
            raise UserError(_("All linked expense sheets are already paid."))

        for sheet in expense_sheets:
            try:
                sheet.sudo().write(
                    {
                        "payment_state": "paid",
                        "state": "done",
                    }
                )
                for expense in sheet.expense_line_ids.filtered(
                    lambda e: e.state in ("approved", "approve", "reported")
                ):
                    expense.sudo().write({"state": "done"})
            except Exception as e:
                _logger.error("Error marking sheet %s as paid: %s", sheet.id, e)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Marked %s expense sheets as paid.") % len(expense_sheets),
                "type": "success",
                "sticky": False,
            },
        }
