from odoo import api, fields, models
import urllib.parse


class QuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    package_type = fields.Selection([('bundle_package', 'Bundle/Package'), ('pallet', 'Pallet'), ('box', 'Box')],
                                    string="Package type", default="bundle_package", readonly=True)
    sale_order_id = fields.Many2one('sale.order')
    picking_id = fields.Many2one('stock.picking')
    customer_id = fields.Many2one('res.partner', string="Customer")
    has_scanned = fields.Boolean(default=False, string="Has scanned?")

    def get_package_encoded_url(self, pack_id, model, url=False):
        """
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18.
            Purpose: To Generate URL when download report.
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if url:
            base_url += url
        else:
            base_url += "/web#id=%s&model=%s&view_type=form" % (pack_id.id, model)
        return urllib.parse.quote(base_url)
