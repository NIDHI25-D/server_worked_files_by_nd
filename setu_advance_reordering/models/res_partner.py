from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    minimum_reorder_amount = fields.Monetary('Minimum Reorder Amount',currency_field='property_purchase_currency_id')
    vendor_rule = fields.Selection([('both', 'BOTH'),
                                    ('minimum_order_qty', 'Minimum Order Qty'),
                                    ('minimum_order_value', 'Minimum Order Value')],
                                   default='minimum_order_qty',
                                   string='Vendor Rule')
    vendor_pricelist_ids = fields.One2many("product.supplierinfo", "partner_id", "Vendor Pricelists")

    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 08/01/25
            Task: Migration to v18 from v16
            Purpose: create activity only for vendor if it create first time to remind his to your AR template are pending as per the 16 enhancement.
        """
        res = super(ResPartner, self).create(vals)
        if res.supplier_rank == 1:
            note = f'New Vendor {res.name}. Create AR Template.'
            activity = self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'res_id': res.id,
                'res_model_id': self.env.ref('base.model_res_partner').id,
                'user_id': self.env.uid,
                'note': note
            })
            activity.action_close_dialog()
        return res

        # note = f'New Vendor {res.name}. Create AR Template.'
        # self.activity_schedule(
        #     'mail.mail_activity_data_todo',
        #     note=note,
        #     date_deadline=fields.Date.today(),
        #     user_id=self.env.uid
        # )
        # return res

    def action_create_ar_template_from_partner(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 08/01/25
            Task: Migration to v18 from v16
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'advance.reorder.planner',
            'view_mode': 'form',
            'target': 'current',
        }
