import binascii
import json
from datetime import datetime, timedelta
import logging
import requests
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    estafeta_shipping_charge_ids = fields.One2many("estafeta.shipping.charge", "picking_id",
                                                   string="Estafeta Rate")
    estafeta_shipping_charge_id = fields.Many2one("estafeta.shipping.charge", string="Estafeta Service")
    estafeta_no_of_packages = fields.Integer(string='Number of Packages', default=1)

    tracking_status_ids = fields.One2many("estafeta.tracking.status", "picking_id", string="Estafeta Treacking Status")
    is_estafeta_carrier = fields.Boolean(string="Is Estafeta Carrier")

    def get_estafeta_rate(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose: Calling to get estafeta charges.
        """
        if self.shipping_carrier_id.is_for_estafeta:
            self.carrier_id.get_estafeta_charges(self)
        else:
            raise ValidationError(_("Estafeta Shipping Id not found"))

    def get_estafeta_tracking_status(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose: Calling to get estafeta provider tracking status.
        """
        if self.delivery_type == "estafeta_provider":
            self.carrier_id and self.carrier_id.estafeta_provider_get_tracking_status(self)
        else:
            raise ValidationError(_("Estafeta status not found"))

    @api.onchange('shipping_carrier_id')
    def onchange_shipping_carrier_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18 Add LTL service to the Estafeta
            shipping integration addon. [https://app.clickup.com/t/86du5cyg7]
            Purpose: set is_estafeta_carrier as per the shipping carrier field is_for_estafeta
        """
        if self.shipping_carrier_id.is_for_estafeta:
            self.is_estafeta_carrier = True
        else:
            self.is_estafeta_carrier = False

    def check_address_details(self, address_id, required_fields):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose:
                check the address of Shipper and Recipient
                param : address_id: res.partner, required_fields: ['zip', 'city', 'country_id', 'street']
                return: missing address message
        """
        res = [field for field in required_fields if not address_id[field]]
        if res:
            return "Missing Values For Address :\n %s" % ", ".join(res).replace("_id", "")

    def estafeta_provider_create_shipment(self, request_type, api_url, request_data, header):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose: Handling the all requests for Estafeta.
        """
        _logger.info("Shipment Request API URL:::: %s" % api_url)
        _logger.info("Shipment Request Data:::: %s" % request_data)
        response_data = requests.request(method=request_type, url=api_url, headers=header, data=request_data)
        if response_data.status_code in [200, 201]:
            response_data = response_data.json()
            _logger.info(">>> Response Data {}".format(response_data))
            return True, response_data
        else:
            return False, response_data.text

    def send_to_shipper(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose: Handling the requests for is_for_estafeta to not perform send_to_shipper.
        """
        self.ensure_one()
        if not self.shipping_carrier_id.is_for_estafeta:
            super().send_to_shipper()

    def button_validate(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 23/04/2025
            Task: Migration from V16 to V18
            Purpose: Processing the packages or palates for Estafeta.
        """
        res = super(StockPicking, self).button_validate()
        for rec in self:
            charges = self.env['estafeta.shipping.charge'].search([('picking_id', '=', rec.id)])
            if isinstance(res,
                          bool) and rec.picking_type_id.code == 'outgoing' and rec.shipping_carrier_id and rec.shipping_carrier_id.is_for_estafeta and charges:
                shipper_address_id = rec.picking_type_id and rec.picking_type_id.warehouse_id and rec.picking_type_id.warehouse_id.partner_id
                recipient_address_id = rec.partner_id
                company_id = rec.company_id
                shipper_address_error = rec.check_address_details(shipper_address_id,
                                                                  ['zip', 'city', 'country_id', 'street'])
                recipient_address_error = rec.check_address_details(recipient_address_id,
                                                                    ['zip', 'city', 'country_id', 'street'])
                if shipper_address_error or recipient_address_error or not rec.shipping_weight:
                    raise ValidationError("%s %s" % (
                        "Shipper Address : %s \n" % (shipper_address_error) if shipper_address_error else "",
                        "Recipient Address : %s \n" % (recipient_address_error) if recipient_address_error else ""
                    ))

                sender_zip = shipper_address_id.zip or ""
                sender_city = shipper_address_id.city or ""
                sender_country_code = shipper_address_id.country_id and shipper_address_id.country_id.l10n_mx_edi_code or ""
                sender_country_code_numeric = shipper_address_id.country_id and shipper_address_id.country_id.code_numeric or ""
                sender_state_code = shipper_address_id.state_id and shipper_address_id.state_id.code or ""
                sender_street = shipper_address_id.street or ""
                sender_street2 = shipper_address_id.street2 or ""
                sender_mobile = shipper_address_id.mobile or ""
                sender_vat = shipper_address_id.vat
                sender_l10n_mx_edi_locality_id = shipper_address_id.l10n_mx_edi_locality_id or ""

                receiver_zip = recipient_address_id.zip or ""
                receiver_city = recipient_address_id.city or ""
                receiver_country_code = recipient_address_id.country_id and recipient_address_id.country_id.l10n_mx_edi_code or ""
                receiver_country_code_numeric = recipient_address_id.country_id and recipient_address_id.country_id.code_numeric or ""
                receiver_state_code = recipient_address_id.state_id and recipient_address_id.state_id.code or ""
                receiver_street = recipient_address_id.street[0:20] or ""
                receiver_street2 = recipient_address_id.street2 or ""
                receiver_phone = recipient_address_id.phone or ""
                receiver_email = recipient_address_id.email or ""
                receiver_mobile = recipient_address_id.mobile or ""
                reciver_l10n_mx_edi_locality_id = recipient_address_id.l10n_mx_edi_locality_id or ""

                package_ids = rec.move_line_ids.mapped('result_package_id')
                without_pallet_packages_ids = package_ids.filtered(lambda x: x.package_type != 'pallet')
                with_pallet_packages_ids = package_ids.filtered(lambda x: x.package_type == 'pallet')
                shipping_data = False
                way_bills = []
                header = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'apikey': company_id.estafeta_label_api_key,
                    'Authorization': "Bearer {}".format(company_id.estafeta_label_api_token)
                }
                api_url = "{0}?outputType={1}&outputGroup={2}&responseMode={3}&printingTemplate={4}".format(
                    company_id.estafeta_label_api_url, rec.shipping_carrier_id.estafeta_output_type,
                    rec.shipping_carrier_id.estafeta_output_group,
                    rec.shipping_carrier_id.estafeta_response_mode, rec.shipping_carrier_id.estafeta_printing_template)
                if without_pallet_packages_ids:
                    default_code = '79' if len(without_pallet_packages_ids) > 1 else '70'
                    try:
                        request_data = json.dumps({
                            "identification": {
                                "suscriberId": company_id.estafeta_suscriber_id,
                                "customerNumber": company_id.estafeta_customer_number
                            },
                            "systemInformation": {
                                "id": company_id.estafeta_id,
                                "name": company_id.estafeta_name,
                                "version": "1.10.20"
                            },
                            "labelDefinition": {
                                "wayBillDocument": {
                                    "content": rec.product_id.name[0:25],
                                    "referenceNumber": rec.name[0:30]
                                },
                                "itemDescription": {
                                    "parcelId": int(rec.shipping_carrier_id.estafeta_parcel_id),
                                    "weight": without_pallet_packages_ids[0].shipping_weight,
                                    "height": round(
                                        rec.shipping_carrier_id.estafeta_provider_package_id and rec.shipping_carrier_id.estafeta_provider_package_id.height or 0),
                                    "length": round(
                                        rec.shipping_carrier_id.estafeta_provider_package_id and rec.shipping_carrier_id.estafeta_provider_package_id.packaging_length or 0),
                                    "width": round(
                                        rec.shipping_carrier_id.estafeta_provider_package_id and rec.shipping_carrier_id.estafeta_provider_package_id.width or 105)
                                },
                                "serviceConfiguration": {
                                    "quantityOfLabels": len(without_pallet_packages_ids),
                                    "serviceTypeId": default_code,
                                    "salesOrganization": company_id.estafeta_sales_organization,
                                    "effectiveDate": (datetime.now() + timedelta(days=15)).strftime("%Y%m%d"),
                                    # "20240216",
                                    "originZipCodeForRouting": sender_zip,  # Shipment’s origin zip code,
                                    "isInsurance": False,
                                    "isReturnDocument": False,
                                },
                                "location": {
                                    "origin": {
                                        "contact": {
                                            "corporateName": shipper_address_id.company_id.name if shipper_address_id.company_id.name else shipper_address_id.name,
                                            "contactName": shipper_address_id.name[0:30],
                                            "cellPhone": company_id.estafeta_sender_phone if company_id else '',
                                            # https://app.clickup.com/t/86dwfyv1m { Issue when multiple transfers validation. }
                                            "email": company_id.estafeta_sender_email if company_id else ''
                                            # https://app.clickup.com/t/86dwfyv1m { Issue when multiple transfers validation. }
                                        },
                                        "address": {
                                            "bUsedCode": False,
                                            "roadTypeAbbName": "C",  # You can use C. or Calle
                                            "roadName": sender_street,
                                            "settlementTypeAbbName": "Col",
                                            "settlementName": shipper_address_id.name,
                                            "stateAbbName": shipper_address_id.state_id.name,
                                            "zipCode": sender_zip,
                                            "settlementTypeCode": None,
                                            "countryCode": sender_country_code_numeric,
                                            "countryName": sender_country_code,
                                            "externalNum": shipper_address_id.street_number
                                        }
                                    },
                                    "destination": {
                                        "isDeliveryToPUDO": False,
                                        "homeAddress": {
                                            "contact": {
                                                "corporateName": recipient_address_id.company_id.name if recipient_address_id.company_id.name else recipient_address_id.name,
                                                "contactName": recipient_address_id.name[0:30],
                                                "cellPhone": recipient_address_id.mobile,
                                                "email": receiver_email
                                            },
                                            "address": {
                                                "bUsedCode": False,
                                                "roadTypeAbbName": "C",  # You can use C. or Calle
                                                "roadName": receiver_street,
                                                "settlementTypeAbbName": "string",
                                                "settlementName": recipient_address_id.name,
                                                "stateAbbName": recipient_address_id.state_id.name,
                                                "zipCode": receiver_zip,
                                                "settlementTypeCode": None,
                                                "countryCode": receiver_country_code_numeric,
                                                "countryName": receiver_country_code,
                                                "externalNum": recipient_address_id.street_number
                                            }
                                        }
                                    }
                                }
                            }
                        })
                        request_type = "POST"
                        response_status, response_data = rec.estafeta_provider_create_shipment(request_type, api_url,
                                                                                               request_data,
                                                                                               header)
                        if response_status and response_data:
                            label_data = response_data.get("data")
                            label_binary_data = binascii.a2b_base64(str(label_data))
                            if not label_data:
                                raise ValidationError(response_data)
                            way_bills = []
                            tracking_code = []
                            trackings = response_data.get("labelPetitionResult") and response_data.get(
                                "labelPetitionResult").get(
                                "elements")
                            for tracking in trackings:
                                way_bills.append(tracking.get("wayBill"))
                                tracking_code.append(tracking.get("trackingCode"))
                            logmessage = "<b>Tracking Number:</b> %s" % (",".join(tracking_code))
                            rec.message_post(body=logmessage,
                                             attachments=[("%s.pdf" % (rec.name), label_binary_data)])
                        else:
                            raise ValidationError(response_data)
                    except Exception as e:
                        raise ValidationError(e)

                if with_pallet_packages_ids:
                    unspsc_code_line_ids = rec.move_line_ids.filtered(
                        lambda line: line.product_id.id in with_pallet_packages_ids.quant_ids.product_id.ids)
                    max_qty_line = max(unspsc_code_line_ids.mapped('qty_done'))
                    unspsc_code_line_ids = unspsc_code_line_ids.filtered(lambda line: line.qty_done == max_qty_line)
                    try:
                        header = {
                            'accept': 'application/json',
                            'Content-Type': 'application/json',
                            'apikey': company_id.estafeta_label_api_key,
                            'Authorization': "Bearer {}".format(company_id.estafeta_label_api_token)
                        }
                        api_url = "{0}?outputType={1}&outputGroup={2}&responseMode={3}".format(
                            # company_id.rest_estafeta_label_api_url, rec.shipping_carrier_id.estafeta_output_type, rec.shipping_carrier_id.estafeta_output_group,
                            company_id.rest_estafeta_label_api_url, 'FILE_PDF',
                            rec.shipping_carrier_id.estafeta_output_group,
                            rec.shipping_carrier_id.estafeta_response_mode)
                        request_data = json.dumps({
                            "identification": {
                                "suscriberId": company_id.estafeta_suscriber_id,
                                "customerNumber": company_id.estafeta_customer_number
                            },
                            "systemInformation": {
                                "id": company_id.estafeta_id,
                                "name": company_id.estafeta_name,
                                "version": "1.10.20"
                            },
                            "labelDefinition": {
                                "wayBillDocument": {
                                    "aditionalInfo": "string",
                                    "content": rec.product_id.name[0:25],
                                    "costCenter": rec.shipping_carrier_id.costcenter,
                                    "customerShipmentId": "",
                                    "referenceNumber": rec.name[0:30],
                                    "groupShipmentId": "",
                                    "pallet": {
                                        "merchandise": "NATIONAL",
                                        "genericContent": unspsc_code_line_ids[0].product_id.unspsc_code_id.name,
                                        "type": "SIMPLE"
                                    }
                                },
                                "itemDescription": {
                                    "parcelId": int(rec.shipping_carrier_id.estafeta_pallet_parcel_id),
                                    "weight": round(sum(with_pallet_packages_ids.mapped('shipping_weight')), 3),
                                    "height": round(
                                        rec.shipping_carrier_id.estafeta_provider_pallet_id and rec.shipping_carrier_id.estafeta_provider_pallet_id.height or 150),
                                    "length": round(
                                        rec.shipping_carrier_id.estafeta_provider_pallet_id and rec.shipping_carrier_id.estafeta_provider_pallet_id.packaging_length or 120),
                                    "width": round(
                                        rec.shipping_carrier_id.estafeta_provider_pallet_id and rec.shipping_carrier_id.estafeta_provider_pallet_id.width or 105),
                                    "merchandises": {
                                        "totalGrossWeight": round(sum(with_pallet_packages_ids.mapped('weight')), 3),
                                        "weightUnitCode": rec.shipping_carrier_id.weightunitcode,
                                        "merchandise": [{
                                            "productServiceCode": rec.shipping_carrier_id.productservicecode,
                                            "merchandiseQuantity": sum(
                                                with_pallet_packages_ids.quant_ids.mapped('quantity')),
                                            "measurementUnitCode": rec.shipping_carrier_id.measurementunitcode,
                                        }]
                                    }
                                },
                                "serviceConfiguration": {
                                    "quantityOfLabels": len(with_pallet_packages_ids),
                                    "serviceTypeId": rec.shipping_carrier_id.estafeta_pallet_service_type_id,
                                    "salesOrganization": company_id.estafeta_sales_organization,
                                    "effectiveDate": (datetime.now() + timedelta(days=15)).strftime("%Y%m%d"),
                                    "originZipCodeForRouting": sender_zip,
                                    "isInsurance": False,
                                    "isReturnDocument": False,
                                },
                                "location": {
                                    "isDRAAlternative": False,
                                    "DRAAlternative": {},
                                    "origin": {
                                        "contact": {
                                            "corporateName": shipper_address_id.company_id.name if shipper_address_id.company_id.name else shipper_address_id.name,
                                            "contactName": shipper_address_id.name[0:30],
                                            "cellPhone": shipper_address_id.mobile,
                                            "email": company_id.estafeta_sender_email if company_id else '',
                                            # https://app.clickup.com/t/86dwfyv1m { Issue when multiple transfers validation. }
                                            "taxPayerCode": shipper_address_id.vat
                                        },
                                        "address": {
                                            "bUsedCode": False,
                                            "roadTypeCode": None,
                                            "roadTypeAbbName": "XX",
                                            "roadName": sender_street,
                                            "townshipCode": None,
                                            "townshipName": "string",
                                            "settlementTypeCode": None,
                                            "settlementTypeAbbName": "string",
                                            "settlementName": shipper_address_id.name,
                                            "stateCode": "",
                                            "stateAbbName": shipper_address_id.state_id.name,
                                            "zipCode": sender_zip,
                                            "countryCode": sender_country_code_numeric,
                                            "countryName": sender_country_code,
                                            "addressReference": None,
                                            "betweenRoadName1": "",
                                            "betweenRoadName2": "",
                                            "latitude": None,
                                            "longitude": None,
                                            "externalNum": shipper_address_id.street_number,
                                            "indoorInformation": shipper_address_id.street_number2,
                                            "nave": rec.shipping_carrier_id.nav,
                                            "platform": rec.shipping_carrier_id.platform,
                                            "localityCode": sender_l10n_mx_edi_locality_id.code,
                                            "localityName": sender_l10n_mx_edi_locality_id.name
                                        }
                                    },
                                    "destination": {
                                        "isDeliveryToPUDO": False,
                                        "deliveryPUDOCode": "",
                                        "homeAddress": {
                                            "contact": {
                                                "corporateName": recipient_address_id.company_id.name if recipient_address_id.company_id.name else recipient_address_id.name,
                                                "contactName": recipient_address_id.name[0:30],
                                                "cellPhone": recipient_address_id.mobile,
                                                "email": receiver_email
                                            },
                                            "address": {
                                                "bUsedCode": False,
                                                "roadTypeCode": None,
                                                "roadTypeAbbName": "XX",
                                                "roadName": receiver_street,
                                                "townshipCode": None,
                                                "townshipName": "string",
                                                "settlementTypeCode": None,
                                                "settlementTypeAbbName": "string",
                                                "settlementName": recipient_address_id.name,
                                                "stateCode": "",
                                                "stateAbbName": recipient_address_id.state_id.name,
                                                "zipCode": receiver_zip,
                                                "countryCode": receiver_country_code_numeric,
                                                "countryName": receiver_country_code,
                                                "addressReference": None,
                                                "betweenRoadName1": "",
                                                "betweenRoadName2": "",
                                                "latitude": None,
                                                "longitude": None,
                                                "externalNum": recipient_address_id.street_number,
                                                "indoorInformation": recipient_address_id.street_number2,
                                                "nave": rec.shipping_carrier_id.nav,
                                                "platform": rec.shipping_carrier_id.platform,
                                                "localityCode": reciver_l10n_mx_edi_locality_id.code if reciver_l10n_mx_edi_locality_id else '',
                                                "localityName": reciver_l10n_mx_edi_locality_id.name if reciver_l10n_mx_edi_locality_id else ''
                                            }
                                        }
                                    },
                                    "notified": None
                                }
                            }
                        })
                        request_type = "POST"
                        response_status, response_data = rec.estafeta_provider_create_shipment(request_type, api_url,
                                                                                               request_data,
                                                                                               header)
                        if response_status and response_data:
                            label_data = response_data.get("data")
                            label_binary_data = binascii.a2b_base64(str(label_data))
                            if not label_data:
                                raise ValidationError(response_data)
                            tracking_code = []
                            trackings = response_data.get("labelPetitionResult") and response_data.get(
                                "labelPetitionResult").get(
                                "elements")
                            for tracking in trackings:
                                way_bills.append(tracking.get("wayBill"))
                                tracking_code.append(tracking.get("trackingCode"))
                            logmessage = "<b>Tracking Number:</b> %s" % (",".join(tracking_code))
                            rec.message_post(body=logmessage,
                                             attachments=[("%s.pdf" % (rec.name), label_binary_data)])
                        else:
                            raise ValidationError(response_data)
                    except Exception as e:
                        raise ValidationError(e)
            elif isinstance(res, bool) and rec.picking_type_id.code == 'outgoing' and rec.is_estafeta_carrier:
                raise ValidationError('Estafeta charges are not found ')
        return res
