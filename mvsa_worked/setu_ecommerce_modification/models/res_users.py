from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def remove_unverified_contacts(self):
        """
            Author: nidhi@setconsulting.com
            Date: 02/09/25
            Task: Archived contacts [https://app.clickup.com/t/86dxk9hmj]
            modified:Removing unverified users and contacts[migration task], only archive contact and user that does not have sale order and not required fields value filled
        """
        portal_group = self.env.ref("base.group_portal")
        users = self.sudo().search([('is_verified_partner', '=', False), ('groups_id', 'in', portal_group.id)])
        for user in users:
            all_partners = self.env['res.partner'].search([('id', 'child_of', user.partner_id.ids)])
            sale_order_ids = self.env['sale.order'].search(
                [('partner_id', 'in', all_partners.ids), ('state', '=', 'sale')])
            fields_to_check = ['vat', 'street', 'country_id', 'name', 'email', 'warehouse_sugerido_id']
            missing_value = [f for f in fields_to_check if not user.partner_id[f]]
            if not sale_order_ids and missing_value:
                user.sudo().write({'active': False})
                user.partner_id.sudo().write({'active': False})
