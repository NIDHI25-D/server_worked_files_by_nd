# -*- coding: utf-8 -*-
from odoo import fields, models


class SetuDisplayMessage(models.TransientModel):
    _name = "setu.display.message.wiz"
    _description = "Message Wizard"

    text = fields.Text(string='Message', translate=True)

    def generated_message(self, message, name='Message/Summary'):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to generate message for ecommerce connector
        :param message:
        :param name:
        :return: wizard with message
        """
        partial_id = self.create({'text': message}).id
        return {
            'name': name,
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'setu.display.message.wiz',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]', }
