from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    change_pricelist_id = fields.Many2one('product.pricelist', string='Repair Order Default Pricelist')

    # def set_values(self):
    #     res = super(ResConfigSettings, self).set_values()
    #     IrDefault = self.env['ir.default'].sudo()
    #     IrDefault.set('res.config.settings', 'change_pricelist_id', self.change_pricelist_id.id or False)
    #     return res
    #
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     IrDefault = self.env['ir.default'].sudo()
    #     change_pricelist_id = IrDefault.get('res.config.settings', 'change_pricelist_id') or False
    #     res.update(change_pricelist_id=change_pricelist_id, )
    #     return res
