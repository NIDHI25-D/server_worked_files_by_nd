from odoo import api, fields, models


class PutInPackPackagesTypeWizards(models.TransientModel):
    _name = 'put.in.pack.package.type.wizards'
    _description = 'PutInPackPackagesTypeWizards'

    package_type = fields.Selection([('bundle_package', 'Bundle/Package'), ('pallet', 'Pallet'), ('box', 'Box')],
                                    string="Package type", ondelete={'bundle_package': 'cascade'})
    packages_shipping_weight = fields.Float(string="Shipping weight")

    def create_package_with_type(self):
        stock_quants_packages_id = self.env['stock.quant.package'].browse(self._context.get('quant_packages_id'))
        stock_picking_id = self.env['stock.picking'].browse(self._context.get('picking_ids'))
        customers_id = self.env['res.partner'].browse(self._context.get('customer_id'))
        stock_quants_packages_id.write({'package_type': self.package_type,
                                        'shipping_weight': self.packages_shipping_weight,
                                        'picking_id': stock_picking_id,
                                        'sale_order_id': stock_picking_id.sale_id,
                                        'customer_id': customers_id})