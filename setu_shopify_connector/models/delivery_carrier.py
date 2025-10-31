# -*- coding: utf-8 -*-

from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    shopify_code = fields.Char(string="Shopify Delivery Code")
    shopify_source = fields.Char(string="Shopify Delivery Source")

    shopify_tracking_provider = fields.Selection([
        ('4PX', '4PX'),
        ('APC', 'APC'),
        ('Amazon Logistics UK', 'Amazon Logistics UK'),
        ('Amazon Logistics US', 'Amazon Logistics US'),
        ('Anjun Logistics', 'Anjun Logistics'),
        ('Australia Post', 'Australia Post'),
        ('Bluedart', 'Bluedart'),
        ('Canada Post', 'Canada Post'),
        ('Canpar', 'Canpar'),
        ('China Post', 'China Post'),
        ('Chukou1', 'Chukou1'),
        ('Correios', 'Correios'),
        ('Couriers Please', 'Couriers Please'),
        ('DHL Express', 'DHL Express'),
        ('DHL eCommerce', 'DHL eCommerce'),
        ('DHL eCommerce Asia', 'DHL eCommerce Asia'),
        ('DPD', 'DPD'),
        ('DPD Local', 'DPD Local'),
        ('DPD UK', 'DPD UK'),
        ('Delhivery', 'Delhivery'),
        ('Eagle', 'Eagle'),
        ('FSC', 'FSC'),
        ('Fastway Australia', 'Fastway Australia'),
        ('FedEx', 'FedEx'),
        ('GLS', 'GLS'),
        ('GLS (US)', 'GLS (US)'),
        ('Globegistics', 'Globegistics'),
        ('Japan Post (EN)', 'Japan Post (EN)'),
        ('Japan Post (JA)', 'Japan Post (JA)'),
        ('La Poste', 'La Poste'),
        ('New Zealand Post', 'New Zealand Post'),
        ('Newgistics', 'Newgistics'),
        ('PostNL', 'PostNL'),
        ('PostNord', 'PostNord'),
        ('Purolator', 'Purolator'),
        ('Royal Mail', 'Royal Mail'),
        ('SF Express', 'SF Express'),
        ('SFC Fulfillment', 'SFC Fulfillment'),
        ('Sagawa (EN)', 'Sagawa (EN)'),
        ('Sagawa (JA)', 'Sagawa (JA)'),
        ('Sendle', 'Sendle'),
        ('Singapore Post', 'Singapore Post'),
        ('StarTrack', 'StarTrack'),
        ('TNT', 'TNT'),
        ('Toll IPEC', 'Toll IPEC'),
        ('UPS', 'UPS'),
        ('USPS', 'USPS'),
        ('Whistl', 'Whistl'),
        ('Yamato (EN)', 'Yamato (EN)'),
        ('Yamato (JA)', 'Yamato (JA)'),
        ('YunExpress', 'YunExpress')
    ])