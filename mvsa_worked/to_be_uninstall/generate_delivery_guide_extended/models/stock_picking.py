# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import re
from datetime import datetime
from odoo.exceptions import ValidationError

CFDI_XSLT_CADENA = 'l10n_mx_edi_stock/data/cadenaoriginal_cartaporte.xslt'


class Picking(models.Model):
    _inherit = 'stock.picking'

    def _l10n_mx_edi_create_delivery_guide(self):
        # res = super(Picking, self)._l10n_mx_edi_create_delivery_guide()
        def format_float(val, digits=2):
            return '%.*f' % (digits, val)

        for record in self:
            name_numbers = list(re.finditer('\d+', record.name))
            mx_tz = self.env['account.move']._l10n_mx_edi_get_cfdi_partner_timezone(
                record.picking_type_id.warehouse_id.partner_id or record.company_id.partner_id)
            date_fmt = '%Y-%m-%dT%H:%M:%S'
            warehouse_zip = record.picking_type_id.warehouse_id.partner_id and record.picking_type_id.warehouse_id.partner_id.zip or record.company_id.zip
            origin_type, origin_uuids = None, []
            if record.l10n_mx_edi_origin and '|' in record.l10n_mx_edi_origin:
                split_origin = record.l10n_mx_edi_origin.split('|')
                if len(split_origin) == 2:
                    origin_type = split_origin[0]
                    origin_uuids = split_origin[1].split(',')
            values = {
                'cfdi_date': datetime.today().astimezone(mx_tz).strftime(date_fmt),
                'scheduled_date': record.scheduled_date.astimezone(mx_tz).strftime(date_fmt),
                'folio_number': name_numbers[-1].group(),
                'origin_type': origin_type,
                'origin_uuids': origin_uuids,
                'serie': re.sub(r'\W+', '', record.name[:name_numbers[-1].start()]),
                'lugar_expedicion': warehouse_zip,
                'supplier': record.company_id,
                'customer': record.partner_id.commercial_partner_id,
                'moves': record.move_ids.filtered(lambda ml: ml.quantity_done > 0),
                'record': record,
                'format_float': format_float,
                'weight_uom': self.env['product.template']._get_weight_uom_id_from_ir_config_parameter(),
            }
            if False in record.l10n_mx_edi_vehicle_id.figure_ids.mapped('type'):
                raise ValidationError(_("Kindly Add or Delete empty Intermediaries line in Vehicle setup"))
            else:
                xml = self._l10n_mx_edi_dg_render(values)
                certificate = record.company_id.l10n_mx_edi_certificate_ids.sudo()._get_valid_certificate()
                if certificate:
                    xml = certificate._certify_and_stamp(xml, self._l10n_mx_edi_get_cadena_xslt())
                return xml