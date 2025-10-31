from odoo import api, fields, models

class ShippingCarrier(models.Model):
    _inherit = 'shipping.carrier'

    estafeta_provider_package_id = fields.Many2one('stock.package.type', string="Package Info", help="Default Package")

    estafeta_parcel_id = fields.Selection([('1', 'Envelope'),
                                           ('4', 'Package'),
                                           ('5', 'Pallet'),
                                           ], string="parcel Id", default='4')
    estafeta_output_type = fields.Selection([('FILE_PDF', 'FILE_PDF'),
                                             ('FILE_PDF_SC', 'FILE_PDF_SC'),
                                             ('FILE_THERMAL_SEQUENCE', 'FILE_THERMAL_SEQUENCE'),
                                             ('SECTION_DOCUMENT', 'SECTION_DOCUMENT')
                                             ], string="Output Type", default='FILE_PDF')
    estafeta_output_group = fields.Selection([('INDIVIDUAL', 'INDIVIDUAL'),
                                              ('SYNC_REFERENCE', 'SYNC_REFERENCE'),
                                              ('REQUEST', 'REQUEST')
                                              ], string="Output Group", default='REQUEST')
    estafeta_response_mode = fields.Selection([('SYNC_INLINE', 'SYNC_INLINE'),
                                               ('SYNC_REFERENCE', 'SYNC_REFERENCE')
                                               ], string="Response Mode", default='SYNC_INLINE')
    estafeta_printing_template = fields.Char(string="Printing Template",
                                             help="The value to be used must be provided by Estafeta Team.")

    estafeta_service_type_id = fields.Char(string="Service Type Id", default='70')
    estafeta_default_service_type_id = fields.Boolean(string="Default Service Type Id", default=False)
    estafeta_pallet_service_type_id = fields.Char(string="Pallet Service Type Id", default='L0')
    productservicecode = fields.Char("Product Service Code", copy=False, default='31162800')
    weightunitcode = fields.Char("Weight Unit Code", copy=False, default='XOC')
    nav = fields.Char("Nav", copy=False, default="NA000")
    platform = fields.Char("Platform", copy=False, default="P000")
    measurementunitcode = fields.Char("Measurement Unit Code", copy=False, default="F63")
    costcenter = fields.Char("Cost Center", copy=False, default="SPMXA12345")
    estafeta_pallet_parcel_id = fields.Selection([('1', 'Envelope'),
                                                  ('4', 'Package'),
                                                  ('5', 'Pallet'),
                                                  ], string="parcel Id", default='5')
    is_for_estafeta = fields.Boolean(string="Use as estafeta rate")
    estafeta_provider_pallet_id = fields.Many2one('stock.package.type', string="Pallet Info", help="Default Package")