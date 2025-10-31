from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class SetuMenuAccess(models.Model):
    _name = "setu.menu.access"
    _description = "Setu Menu Access Description"

    name = fields.Char("Model", )
    access_id = fields.Many2one(comodel_name="setu.access.rights")
    menu_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'said', 'menu_id',
                                string='Hide Menus')
    all_menu_ids = fields.Many2many('ir.ui.menu', 'ir_ui_all_hide_menu_rel', 'asaid', 'menu_id',
                                    string='All Menus', compute='_compute_all_menu_ids', store=True)

    @api.depends('menu_ids')
    def _compute_all_menu_ids(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 17/03/25
            Task: Migration from V16 to V18
            Purpose: It will return the child menu ids of a selected menu from the setu access rights records.
        """
        _logger.debug("Compute _compute_all_menu_ids method start")
        for rec in self:
            rec.all_menu_ids = rec.get_child_menu_ids(rec.menu_ids)
        _logger.debug("Compute _compute_all_menu_ids method end")

    def get_child_menu_ids(self, menu_ids):
        """
            Authour:yash@setconsulting
            Date: 13/02/23
            Task: 16 Migration
            Purpose: Get childs menu ids
        """
        parent_ids = menu_ids.filtered(lambda x: not x.action)
        if parent_ids:
            x_menu_ids = menu_ids.search([('parent_id', 'in', parent_ids.ids)])
            menu_ids += self.get_child_menu_ids(x_menu_ids)
        return menu_ids
