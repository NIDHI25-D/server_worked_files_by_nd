from odoo import api, fields, models


class ChooseDeliveryPackage(models.TransientModel):
    _inherit = 'choose.delivery.package'

    package_type = fields.Selection([('bundle_package', 'Bundle/Package'), ('pallet', 'Pallet'), ('box', 'Box')],
                                    string="Package type")
    carrier_id = fields.Many2one("delivery.carrier","carrier",related="picking_id.carrier_id")

    def action_put_in_pack(self):
        """
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18 (Massive package button).
            Purpose: This method is overwrite only when the method is called from Massive Package.Its overwrite because we need to
                     set shipping_weight per product in the package.
        """
        if self._context.get('massive_package'):
            self = self.with_context(massive_package_method=True,method_massive_package=self.package_type)
            move_line_ids = self.picking_id._package_move_lines(batch_pack=self.env.context.get("batch_pack"))
            delivery_package = self.picking_id._put_in_pack(move_line_ids)
            if self.delivery_package_type_id:
                delivery_package.package_type_id = self.delivery_package_type_id
            if self.shipping_weight:
                for package in delivery_package:
                    product_id = package.picking_id.move_line_ids.filtered(lambda x : x.result_package_id.id == package.id).product_id
                    package.shipping_weight = product_id.weight
        else :
            return super(ChooseDeliveryPackage, self.with_context(package_type=self.package_type)).action_put_in_pack()

