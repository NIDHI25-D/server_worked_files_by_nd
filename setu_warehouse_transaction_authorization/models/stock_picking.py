from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'StockPicking'

    @api.constrains('location_id', 'location_dest_id')
    def onchange_method_for_internal_transer(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 24/12/24
            Task: Migration from V16 to V18
            Purpose: To raise error if there is no configuration like the below
                     user -- test
                     warehouse -- test warehouse 1
                     location -- test location 1, test location 2

                     Internal transfer -- warehouse -- test warehouse 1
                                       -- destination location -- test location 3
        """
        if self.location_id and self.location_dest_id and not self.location_dest_id.bypass_authorization_for_internal:
            if self.picking_type_id and self.picking_type_id.code == 'internal' and not (
            self.user_id.has_group("stock_inv_ext.group_stock_inventory_supervisor") if self.user_id else False):
                cur_usr = self.env['res.users'].browse(self.env.uid_origin) if self.env.uid_origin else self.env.user
                source_location = self.picking_type_id.warehouse_id
                user_record_set = source_location and source_location.sudo().warehouse_authorization_ids.filtered(
                    lambda x: x.user_id == cur_usr) or False
                location_id = []
                if user_record_set:
                    location_id = [rec.id for rec in user_record_set.mapped('location_ids')]
                    location_id.extend([rec.id for rec in user_record_set.location_ids.mapped('child_ids')])
                if not user_record_set or (user_record_set and self.location_dest_id.id not in location_id):
                    raise ValidationError(
                        _("You are not allowed to do this transfer for location '%s' \nPlease contact your administrator") % (
                            self.location_dest_id.complete_name))
        return {}
