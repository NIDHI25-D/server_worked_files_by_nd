from odoo import fields, models, api


class setupriceupdatesettings(models.TransientModel):
    _inherit = 'res.config.settings'

    level = fields.Many2one('competition.level', config_parameter='setu_price_update.level')
    range1 = fields.Integer(config_parameter='setu_price_update.range1')
    range2 = fields.Integer(config_parameter='setu_price_update.range2')
    import_factor = fields.Float(config_parameter='setu_price_update.import_factor')
    responsible_id = fields.Many2one('res.users', config_parameter='setu_price_update.responsible_id')
    exchange_rate = fields.Float(config_parameter='setu_price_update.exchange_rate')
    discount_ids = fields.Many2many('product.price.update.discounts', 'res_setting_discount_rel', 'res_setting_id',
                                    'disc_id', string="Discounts")

    @api.model
    def get_values(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Purpose: get the value of discount_ids in settings.
        """
        res = super(setupriceupdatesettings, self).get_values()
        discount_ids = self.env['ir.config_parameter'].sudo().get_param('setu_price_update.discount_ids')
        if discount_ids:
            res['discount_ids'] = [(6, 0, eval(discount_ids))]
        return res

    def set_values(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/12/24
            Purpose: set the value of discount_ids in settings to save the record of many2many field.
        """
        res = super(setupriceupdatesettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'setu_price_update.discount_ids',
            self.discount_ids.ids)
        return res
