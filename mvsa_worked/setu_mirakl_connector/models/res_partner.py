from odoo import models,_,fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer_from_mirakl = fields.Boolean(string='Mirakl Customer',default=False,copy=False)
    mirakl_customer_id = fields.Integer(string="Customer ID for Mirakl Connector")


    def find_existing_mirakl_customer(self, mirakl_customer_id, multi_ecommerce_connector_id):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: find the customer is exists or not.
            return : partner if found.
        """
        partner_id = self.search([("mirakl_customer_id", "=", mirakl_customer_id), ("multi_ecommerce_connector_id", "=", multi_ecommerce_connector_id and multi_ecommerce_connector_id.id)],  limit=1)
        if partner_id:
            return partner_id

    def create_main_mirakl_customer(self, multi_ecommerce_connector_id,vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: creates partner from the data of the order.
            return : partner's record.
        """
        if multi_ecommerce_connector_id == multi_ecommerce_connector_id:
            customer_data = vals.get('customer')
            customer_shipping_address = customer_data.get('shipping_address')
            partner_record = self.create({
                'name': f"{customer_data.get('firstname')} {customer_data.get('lastname')}",
                'email': vals.get('customer_notification_email'),
                'city': customer_shipping_address.get('city') if customer_shipping_address else None,
                'country_id': self.env['res.country'].search(
                    [('code', '=', customer_shipping_address.get('country'))]).id if customer_shipping_address else None,
                'street': customer_shipping_address.get('street_1') if customer_shipping_address else None,
                'street2': customer_shipping_address.get('street_2') if customer_shipping_address else None,
                'zip': customer_shipping_address.get('zip_code') if customer_shipping_address else None,
            })
            return partner_record