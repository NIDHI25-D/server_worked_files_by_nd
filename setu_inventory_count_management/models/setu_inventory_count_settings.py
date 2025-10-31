# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InventoryCountSettings(models.Model):
    _name = 'setu.inventory.count.settings'
    _description = """ This model is used to Auto Adjust Inventory."""

    auto_inventory_adjustment = fields.Boolean(string="Auto Inventory Adjustment?")

    name = fields.Char(string="Inventory Count Configuration", default="Inventory Count Configuration")

    @api.model
    def open_record_action(self):
        view_id = self.env.ref('setu_inventory_count_management.setu_inventory_count_settings_view_form').id
        record = self.env['setu.inventory.count.settings'].search([]).id
        return {'type': 'ir.actions.act_window',
                'name': _('Settings - Inventory Count'),
                'res_model': 'setu.inventory.count.settings',
                'target': 'current',
                'res_id': record,
                'view_mode': 'form',
                'views': [[view_id, 'form']]}
