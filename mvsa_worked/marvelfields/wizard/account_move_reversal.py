# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    is_marvelsa_wallet = fields.Boolean(string="Marvelsa Wallet")
    wallet_type = fields.Selection(selection=[('credit_note', 'Credit Note'), ('marvelsa_wallet', 'Marvelsa Wallet')],
                                   default='credit_note')

    @api.model
    def default_get(self, fields):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/01/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86du9drak)
            Purpose: to implement the functionality of Marvelsa Wallet which is at res partner leval configration
            to identify the type of wallet.
        """
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get(
            'active_model') == 'account.move' else self.env['account.move']
        if len(move_ids) > 1:
            res['wallet_type'] = False
        else:
            if move_ids.partner_id.bonus_type == 'marvelsa_wallet':
                res['wallet_type'] = move_ids.partner_id.bonus_type
        return res
