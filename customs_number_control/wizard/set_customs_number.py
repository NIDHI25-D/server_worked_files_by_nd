# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons.l10n_mx_edi_extended.models.account_move import CUSTOM_NUMBERS_PATTERN
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class SetCustomsNumber(models.Model):
    _name = 'set.customs.number'
    _description = "Set Customs Number"

    line_customs_number = fields.Char('Customs Number',
                                      help='Optional field for entering the customs information in the case '
                                           'of first-hand sales of imported goods or in the case of foreign trade'
                                           ' operations with goods or services.\n'
                                           'The format must be:\n'
                                           ' - 2 digits of the year of validation followed by two spaces.\n'
                                           ' - 2 digits of customs clearance followed by two spaces.\n'
                                           ' - 4 digits of the serial number followed by two spaces.\n'
                                           ' - 1 digit corresponding to the last digit of the current year, '
                                           'except in case of a consolidated customs initiated in the previous '
                                           'year of the original request for a rectification.\n'
                                           ' - 6 digits of the progressive numbering of the custom.',
                                      size=21, copy=False, tracking=True)

    # @api.constrains('line_customs_number')
    # def _check_line_customs_number(self):
    #     help_message = self._fields['line_customs_number'].help.split('\n', 1)[1]
    #     for inventory in self:
    #         if not inventory.line_customs_number:
    #             continue
    #         custom_number = inventory.line_customs_number.strip()
    #         if not CUSTOM_NUMBERS_PATTERN.match(custom_number):
    #             raise ValidationError(_("Error!, The format of the customs number is incorrect. \n%s\n"
    #                                     "For example: 15  48  3009  0001234") % help_message)
    #
    # def create_line_customs_number(self):
    #     current_stock_move_line_id = self.env['stock.move.line'].browse(self._context.get('active_id'))
    #     if not current_stock_move_line_id.customs_number:
    #         current_stock_move_line_id.customs_number = self.line_customs_number
    #     else:
    #         raise UserError(_("Customs number is already set in this stock move line."))
