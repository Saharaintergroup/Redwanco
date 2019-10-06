# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons import decimal_precision as dp

class PatchPayment(models.Model):
    _name = 'patch.payment'
    _description = 'Patch Payment'
    
    name = fields.Char('Name', readonly=True , default=lambda x: str('New')) #default=default_randint_value
    sales_agent = fields.Many2one('sales.agent', string='Sales Agent Patch')
    patch_payment_line = fields.One2many('patch.payment.line', 'patch_payment', string='Sales Agent')
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('patch.payment') or _('New')                
            result = super(PatchPayment, self).create(vals)
            return result



    @api.one
    def ConfirmPost(self):
        for line in self.patch_payment_line:
            date = self.payment_date
            salesagent = self.sales_agent
            paymet_send = line.lines_pay_and_reconcile(date,salesagent)
        self.write({
            'state': 'confirmed'
            })


    @api.multi
    def action_view_patch_payments(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        return {
            'name': _('Patch Account Payments'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('patch_ref', '=', self.name)],
        }



class PatchPaymentLine(models.Model):
    _name = 'patch.payment.line'
    _description = 'Patch Payment Line'

    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    name = fields.Char('Name', readonly=True , default=lambda x: str('New')) #default=default_randint_value
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    patch_payment = fields.Many2one('patch.payment', string='patch_payment')
    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_transaction_rel', 'transaction_id', 'invoice_id',
                                   string='Invoices', copy=False, readonly=True)
    patch_ref = fields.Char(string='Patch Reference' , compute='_compute_patch_ref')


    @api.one
    def _compute_patch_ref(self):
        for ref in self.patch_payment:
            self.patch_ref = ref.name



    @api.multi
    def _prepare_lines_payment_vals(self, date ,salesagent):
        self.ensure_one()
        return {
            'state': 'draft',
            'amount': self.amount,
            'payment_type': 'inbound',
            'payment_date': date,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'agent_id': salesagent.id,
            'partner_type': 'customer',
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'payment_token_id': None,
            'patch_ref': self.patch_ref,
            'communication': self.communication,
            'writeoff_account_id': False,
        }


    @api.multi
    def lines_pay_and_reconcile(self,date,salesagent):
        newdate = date
        newsales_agent = salesagent
        payment_vals = self._prepare_lines_payment_vals(newdate,newsales_agent)
        payment = self.env['account.payment'].create(payment_vals)
        payment.postdraft()

        return True






class account_payment(models.Model):
    _name = "account.payment"
    _inherit = 'account.payment'

    patch_ref = fields.Char(string='Patch Payment Reference')

    @api.multi
    def postdraft(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'draft', 'move_name': move.name})
        return True
