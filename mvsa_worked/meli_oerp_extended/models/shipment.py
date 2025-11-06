from odoo import fields, osv, models, api, SUPERUSER_ID
import logging

_logger = logging.getLogger('shipping_address_adding_zip')


class mercadolibre_shipment(models.Model):
    _inherit = "mercadolibre.shipment"

    def partner_delivery_id(self, partner_id=None, Receiver=None, config=None):
        """
              Author: jay.garach@setuconsulting.com
              Date: 10/04/25
              Task: Migration from V16 to V18
              Purpose: to add the postal code while creating the delivery address through mercadolibre.
        """
        partner_shipping_id = super(mercadolibre_shipment, self).partner_delivery_id(partner_id, Receiver,  config)
        if Receiver and ('neighborhood' and 'zip_code' in Receiver):
            try:
                zip_code = int(Receiver.get('zip_code', ''))
            except:
                _logger.info('Can\'t set Postal Code because of Zip %s and Colony %s are blank.',
                             Receiver.get('zip_code', ''), Receiver.get('neighborhood', '').get('name', ''))
                zip_code = False
            if zip_code:
                city_name = Receiver.get('city', '').get('name', '')
                try:
                    state_code = Receiver.get('state', '').get('id', '').split('-')[1]
                except:
                    state_code = Receiver.get('state', '').get('id', '')
                country_code = Receiver.get('country', '').get('id', '')
                country_id = self.env["res.country"]
                state_id = self.env["res.country.state"]
                if state_code and country_code:
                    country_id = self.env["res.country"].search([('code', '=', country_code)])
                    state_id = self.env["res.country.state"].search(
                        [('code', '=', state_code), ('country_id', '=', country_id.id)])
                city_id = self.env["res.city"].search(
                    [('name', '=', city_name), ('state_id', '=', state_id.id), ('country_id', '=', country_id.id)])
                if not city_id and state_id and country_id:
                    city_id = self.env['res.city'].create(
                        {'name': city_name, 'state_id': state_id.id, 'country_id': country_id.id})
                sepomex_id = self.env["sepomex.res.colony"].sudo().search(
                    [('postal_code', '=', Receiver.get('zip_code', '')),
                     ('name', '=', Receiver.get('neighborhood', '').get('name', ''))])
                if not sepomex_id:
                    sepomex_id = self.env["sepomex.res.colony"].sudo().create({
                        'postal_code': Receiver.get('zip_code', ''),
                        'name': Receiver.get('neighborhood', '').get('name', ''),
                        'city_id': city_id.id if city_id else False
                    })
                    sepomex_id._compute_new_display_name()
                if sepomex_id:
                    partner_shipping_id.write({'postal_code_id': sepomex_id.id})
                    partner_shipping_id._onchange_postal_code_id()
        return partner_shipping_id