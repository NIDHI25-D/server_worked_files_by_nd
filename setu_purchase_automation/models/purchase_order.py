# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import datetime
import logging
import requests
import base64
import json
import pytz
from markupsafe import Markup

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    extended_state = fields.Selection(selection=[('in_prod', 'In Production'),
                                                 ('po_ready', 'Purchase Order Ready'),
                                                 ('in_transit', 'In Transit'),
                                                 ('in_cc', 'In Custom Clearance'),
                                                 ('dispached', 'Dispatched'),
                                                 ('collected', 'Collected'),
                                                 ('in_yard', 'In Yard'),
                                                 ('counting', 'Counting'),
                                                 ('received', 'Received'),
                                                 ('wait_for_expences', 'Waiting For Expenses'),
                                                 ('finalized_purchase_order', 'Finalized purchase Order'),
                                                 ('on_hold', 'On Hold'),
                                                 ('cancel', 'Canceled')],
                                      string="Purchase Status")
    purchase_company = fields.Many2one('res.company', string="Company")
    bl_date = fields.Datetime("BL Date")
    bl_date_at_sight = fields.Datetime("BL Date at Sight")
    date_of_issue_loc = fields.Datetime("Date of Issue Letter of Credit")
    due_date_of_loc = fields.Datetime("Due Date of Letter of Credit")
    ref_of_loc = fields.Char("Reference of Letter of Credit")
    customs = fields.Many2one('custom.cateloges', string="Customs")
    customs_agency = fields.Many2one('custom.agency', string="Custom agency", domain="[('customs','=',customs)]")
    carrier_type = fields.Selection([('int_transport', 'Internal Transport'),
                                     ('ext_transport', 'External Transport')], string="Carrier Type")
    carrier = fields.Many2one('purchase.carriers', string="Carrier")
    payment_status = fields.Selection(selection=[('open', 'Open'),
                                                 ('part_paid', 'Partially paid'),
                                                 ('fully_paid', 'Fully paid')],
                                      string="Payment Status", compute='_compute_payment_status', store=True)
    loading_port_related_tp_partner = fields.Many2many(related="partner_id.departure_shipment_ports_ids")
    loading_port = fields.Many2one('loading.port.cateloges', string="Loading Port")

    vendor_bill_date = fields.Datetime("Vendor Bill Date")
    merchandise_ready_date = fields.Datetime(string="Merchandise Ready Date")
    etd_date = fields.Datetime("ATD Date")
    etd_date_not_edit = fields.Boolean(string="etd lock/unlock", default=False)
    eta_date = fields.Datetime("ATA Date")
    eta_date_not_edit = fields.Boolean(string="eta lock/unlock", default=False)
    custom_clearance_date = fields.Datetime("Customs Clearance Date")
    tax_pay_date = fields.Datetime("Tax Payment Date")
    sea_freight_amount = fields.Float("Sea Freight Amount")
    cc_procedure_dta = fields.Float("Customs clearance procedure(DTA)")
    in_yard_date = fields.Datetime("In Yard Date")
    collected_date = fields.Datetime("Collected Date")
    collected_date_not_edit = fields.Boolean(string="Collected Date Lock/Unlock", default=False)
    counting_date = fields.Datetime("Counting Date")
    received_date = fields.Datetime("Received Date")
    waiting_for_expences = fields.Boolean("Waiting for Expenses", default=False)
    finalized_purchase_order = fields.Boolean("Finalized Purchase Order", default=False)
    associate_order_ids = fields.One2many('associate.purchase.order.with.bank.statement', 'purchase_order_id')
    related_statement_ids = fields.Many2many('account.bank.statement.line', compute='_get_statements')

    last_adv_payment_related_date = fields.Date(string="Last Adv. payment Date",
                                                compute='_compute_related_payment_info')
    total_adv_related_payment = fields.Float("Adv. related payment")
    qty_adv_related_payment = fields.Float("Quantity of advance payments")
    balance_amount = fields.Float("Balance Amount")
    average_price_difference = fields.Float(
        compute='_compute_average_price_difference',
        string='Average Price Difference (%)',
        store=True
    )
    forwarder = fields.Many2one('preorder.forwarder', string="Forwarder")
    vessela = fields.Char(string="Vessela")
    container_number = fields.Char(string="Container Number")
    cubic_meters = fields.Char(string="Cubic Meters")
    bank_of_letter_of_credit = fields.Char(string="Bank Of Letter Of Credit")
    delivery_date = fields.Date(string='Delivery Date')
    container_quantity = fields.Integer("Container Quantity", default=0)
    container_type = fields.Selection(
        [('20_feet', '20 Feet'), ('40_feet', '40 Feet'), ('consolidated', 'Consolidated')], string="Container Type")
    on_hold = fields.Boolean(string='On Hold')
    extended_state_origin = fields.Selection(selection=[('in_prod', 'In Production'),
                                                        ('po_ready', 'Purchase Order Ready'),
                                                        ('in_transit', 'In Transit'),
                                                        ('in_cc', 'In Custom Clearance'),
                                                        ('dispached', 'Dispatched'),
                                                        ('collected', 'Collected'),
                                                        ('in_yard', 'In Yard'),
                                                        ('counting', 'Counting'),
                                                        ('received', 'Received'),
                                                        ('wait_for_expences', 'Waiting For Expenses'),
                                                        ('finalized_purchase_order', 'Finalized purchase Order'),
                                                        ('on_hold', 'On Hold'),
                                                        ('cancel', 'Canceled')],
                                             string="Purchase Status Origin")
    total_iva = fields.Float(string='Total Importation IVA', compute='_compute_average_iva_igi', store=True)
    total_igi = fields.Float(string='Total IGI', compute='_compute_average_iva_igi', store=True)
    empty_return_date = fields.Datetime(string="Empty return date")
    henco_reference = fields.Char(string="Henco Reference")
    freight_cost = fields.Monetary('Freight Cost')
    voyage = fields.Char(string="Voyage")
    henco_etd_date = fields.Datetime("ETD Date")
    henco_eta_date = fields.Datetime("ETA Date")
    arrival_date_history_ids = fields.One2many('arrival.date.history', 'purchase_order_id',
                                               string="Arrival Date History")

    receiving_warehouse_id =  fields.Many2one('stock.warehouse',string="Receiving warehouse")
    inventory_count_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ],string='Inventory count priority')

    @api.depends('order_line.percentage_price_difference')
    def _compute_average_price_difference(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: to set the value of Average Price Difference (%) when multiple purchase order line.
        """
        for order in self:
            total_price_difference = sum(line.percentage_price_difference for line in order.order_line)
            if order.order_line:
                order.average_price_difference = total_price_difference / len(order.order_line)
            else:
                order.average_price_difference = 0.0

    def _compute_related_payment_info(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: calculate the Last Adv. payment Date from the associate bank statement.
        """
        _logger.debug("Compute _compute_related_payment_info method start")
        for rec in self:
            max_date = rec.related_statement_ids._origin.mapped('associate_purchase_order_ids').filtered(
                lambda po_bs: po_bs.purchase_order_id.id == rec._origin.id).mapped('statement_line_id.date')
            if max_date:
                rec.last_adv_payment_related_date = max(max_date)
            else:
                rec.last_adv_payment_related_date = None
            rec.total_adv_related_payment = abs(sum(
                rec.related_statement_ids._origin.mapped('associate_purchase_order_ids').filtered(
                    lambda po_bs: po_bs.purchase_order_id.id == rec._origin.id).mapped('signed_amount')))
            rec.qty_adv_related_payment = len(rec.related_statement_ids._origin)
            rec.balance_amount = rec.amount_total - abs(sum(
                rec.related_statement_ids._origin.mapped('associate_purchase_order_ids').filtered(
                    lambda po_bs: po_bs.purchase_order_id.id == rec._origin.id).mapped('signed_amount')))
        _logger.debug("Compute _compute_related_payment_info method end")

    def _get_statements(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: set related statement from the associate bank statement.
        """
        for order in self:
            order.related_statement_ids = order.associate_order_ids.statement_line_id.ids

    def update_cc_procedure_dta(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: calculate the field Customs clearance procedure(DTA) from the button.
        """
        self.cc_procedure_dta = (self.amount_total + self.sea_freight_amount) * 0.008

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: set the extended_state field as per the fulfillment of the condition, also set the values of the Arrival Dates History tab.
        """
        for rec in self:
            if rec.state == 'purchase' and not rec.extended_state:
                vals.update({'extended_state': 'in_prod'})
            if rec.extended_state == 'counting' and all(
                    picking.state in ['done', 'cancel'] for picking in self.picking_ids):
                vals.update({'extended_state': 'received'})
            if vals.get('date_planned', False):
                last_arrival_date = rec.date_planned
                vals['arrival_date_history_ids'] = [(0, 0, {'update_date': datetime.date.today(), 'last_arrival_date': last_arrival_date})]
        return super(PurchaseOrder, self).write(vals)

    @api.depends('related_statement_ids')
    def _compute_payment_status(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: set payment status from related statement.
        """
        _logger.debug("Compute _compute_payment_status method start")
        for po in self:

            payments_done = sum(list(map(abs, po.related_statement_ids.mapped('associate_purchase_order_ids').filtered(
                lambda po_bs: po_bs.purchase_order_id.id == po.id).mapped('signed_amount'))))
            if payments_done == 0:
                po.payment_status = 'open'
            elif abs(payments_done) > 0 and (abs(payments_done) < po.amount_total):
                po.payment_status = 'part_paid'
            else:
                po.payment_status = 'fully_paid'
        _logger.debug("Compute _compute_payment_status method end")

    @api.onchange('partner_id','eta_date','henco_eta_date')
    def onchange_method_for_partner_id(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: change Expected Arrival from the ETA date and the configuration at the settings Expected Arrival Date Automation.
                     calculation Expected Arrival Date Automation + ETA date.
        """
        tax_payment_days_configures = self.env['ir.config_parameter'].sudo().get_param(
            'setu_purchase_automation.po_tax_payment_days_configures')
        po_expected_arrival_date_automation = int(self.env['ir.config_parameter'].sudo().get_param(
            'setu_purchase_automation.po_expected_arrival_date_automation'))
        cal_tax_payment_date = False
        if self.eta_date:
            cal_tax_payment_date = self.eta_date + datetime.timedelta(days=int(tax_payment_days_configures))
        if self.henco_eta_date:  #TASK : Expected Arrival field automation functionality update.
            self.date_planned = self.henco_eta_date + datetime.timedelta(days=po_expected_arrival_date_automation)
        return {'value': {'loading_port': False}}

    @api.onchange('merchandise_ready_date', 'etd_date', 'etd_date_not_edit', 'eta_date', 'eta_date_not_edit',
                  'custom_clearance_date', 'collected_date', 'in_yard_date', 'collected_date_not_edit',
                  'counting_date', 'received_date', 'waiting_for_expences', 'finalized_purchase_order')
    def onchange_method(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: automation of the field extended_state as per the condition.
        """
        if self.extended_state == 'in_prod' and self.merchandise_ready_date:
            self._origin.sudo().update({'extended_state': 'po_ready'})
        elif self.extended_state == 'po_ready' and self.etd_date and self.etd_date_not_edit:
            self._origin.sudo().update({'extended_state': 'in_transit'})
        elif self.extended_state == 'in_transit' and self.eta_date and self.eta_date_not_edit:
            self._origin.sudo().update({'extended_state': 'in_cc'})
        elif self.extended_state == 'in_cc':
            self._origin.sudo().update({'extended_state': 'dispached'})
        elif self.extended_state == 'dispached' and self.in_yard_date:
            self._origin.sudo().update({'extended_state': 'in_yard'})
        elif self.extended_state == 'in_yard' and self.collected_date and self.collected_date_not_edit:
            self._origin.sudo().update({'extended_state': 'collected'})
        elif self.extended_state == 'collected' and self.counting_date:
            self._origin.sudo().update({'extended_state': 'counting'})
        elif self.finalized_purchase_order:
            self.extended_state = 'finalized_purchase_order'
            # self._origin.sudo().update({'extended_state': 'finalized_purchase_order'})

    @api.onchange('on_hold')
    def onchange_on_hand(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: if field On Hold are checked then changed the field extended_state to the on_hold.
        """
        if self.on_hold:
            self._origin.sudo().update({'extended_state_origin': self.extended_state or False})
            self._origin.sudo().update({'extended_state': 'on_hold'})
        else:
            self._origin.sudo().update({'extended_state': self.extended_state_origin or False})

    def button_cancel(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: if cancel the order then changed the field extended_state to the cancel.
        """
        res = super().button_cancel()
        self.extended_state = 'cancel'
        return res

    def button_draft(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: if reset to draft the order then false the extended_state if it is in on_hold state.
        """
        res = super().button_draft()
        if self.extended_state != 'on_hold':
            self.extended_state = ''
        return res

    @api.depends('order_line.product_id', 'order_line.price_subtotal')
    def _compute_average_iva_igi(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose: calculate the field Total Importation IVA and Total IGI from the order line.
        """
        average_iva = []
        average_igi = []
        for line in self.order_line:
            if line.igi > 0:
                average_igi.append(line.igi)
            if line.iva > 0:
                average_iva.append(line.iva)
        self.total_igi = sum(average_igi)
        self.total_iva = sum(average_iva)

    def set_henco_api_data(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 30/01/25
            Task: Migration to v18 from v16
            Purpose:This method is called via cron. this method will update respected fields if the mentioned henco reference is successfully connected.
                    This will work only for the purchase orders, which are in state done or purchase, arrival date is not set, and henco reference does exist.

            Pre-define parameters where given which need to be set in the Settings and postman(to check):
            API : https://funciones.henco.com.mx/EpicorLive/api/v2/efx/HCO/appclients/OpsByCustomer
            BODY : Company : HCO , Level : Container, Customernum : 11960 , LineType : OCEAN
            Headers : x-api-key : DRxOd8aFYQdAsEaBd1CyASkLfpKJqNfpLVwXRn58Sxp60
            Authorization : Basic Auth : username --> appUserMarvel , password --> R*T9K2p%vDw^zLG8
        """
        api_url = self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_api_url', default='')

        if api_url:
            try:
                purchase_order_records = self.search([]).filtered(lambda x:x.henco_reference and x.state in ['done','purchase'] and x.effective_date == False)
                _logger.info("Henco API : Total Purchase Orders {}".format(purchase_order_records))
                for purchase_ord in purchase_order_records :
                    user_pass = "{}:{}".format(self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_username', default=''),
                                                self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_password', default=''))
                    encoded_credentials = base64.b64encode(user_pass.encode()).decode('utf-8')
                    prod_henco_ref = purchase_ord.henco_reference
                    header = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'x-api-key': self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_x_api_key', default=''),
                        'Authorization':"Basic {}".format(encoded_credentials)
                    }
                    api_url = api_url
                    # Body
                    request_data = json.dumps({
                        "Company": self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_company', default=''),
                        "CustomerNum":int(self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_customernum')) or 0,
                        "LineType": self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_linetype', default=''),
                        "Level": self.env['ir.config_parameter'].sudo().get_param('setu_purchase_automation.henco_level', default=''),
                        "HencoReference":prod_henco_ref
                    })
                    request_type = "POST"
                    response_status, response_data = self.data_of_henco_api(request_type, api_url, request_data, header)
                    if response_status and response_data:
                        if purchase_ord:
                            shipments = response_data.get('Shipments')
                            if shipments:
                                shipment_detail = shipments.get('ShipmentDetail')[0]
                                # Converting dates to the correct format
                                def convert_date(date_str):
                                    return pytz.timezone("America/Mexico_City").localize(datetime.datetime.strptime(date_str, '%d/%m/%Y'),is_dst=None).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')if date_str else False
                                purchase_ord.update(
                                    {'merchandise_ready_date': convert_date(shipment_detail.get('CRD')),
                                     'vessela': shipment_detail.get('Vessel'),
                                     'henco_etd_date': convert_date(shipment_detail.get('ETD')),
                                     'etd_date': convert_date(shipment_detail.get('ActualETD')),
                                     'henco_eta_date': convert_date(shipment_detail.get('ETA')),
                                     'eta_date': convert_date(shipment_detail.get('CYDate')),
                                     'freight_cost': shipment_detail.get('QuotePrice'),
                                     'container_number': shipment_detail.get('ContainerNum'),
                                     'voyage': shipment_detail.get('Voyage')
                                     })
                                purchase_ord.onchange_method_for_partner_id()
                                purchase_ord.onchange_date_planned()
                                _logger.info("Fields were updated for the Purchase Order of Henco:{} \n Henco Reference {}".format(purchase_ord,
                                                                                                prod_henco_ref))
                                purchase_ord.message_post(body=Markup(_(
                                    "Purchase Order Rec: %s <br> Merchandise Ready Date: %s <br> Vessel : %s <br> ETD Date : %s <br> ATD Date : %s <br> ETA Date : %s <br> ATA Date : %s <br> Freight Cost : %s <br> Container Number : %s <br> Voyage :%s ") % (
                                                                         purchase_ord.name,
                                                                         purchase_ord.merchandise_ready_date.date() if purchase_ord.merchandise_ready_date else purchase_ord.merchandise_ready_date,
                                                                         purchase_ord.vessela,
                                                                         purchase_ord.henco_etd_date.date() if purchase_ord.henco_etd_date else purchase_ord.henco_etd_date,
                                                                         purchase_ord.etd_date.date() if purchase_ord.etd_date else purchase_ord.etd_date,
                                                                         purchase_ord.henco_eta_date.date() if purchase_ord.henco_eta_date else purchase_ord.henco_eta_date,
                                                                         purchase_ord.eta_date.date() if purchase_ord.eta_date else purchase_ord.eta_date,
                                                                         purchase_ord.freight_cost,
                                                                         purchase_ord.container_number,
                                                                         purchase_ord.voyage)))
                            else :
                                _logger.info("No data for Purchase order {} for Henco Api: {}".format(purchase_ord,prod_henco_ref))
                        else :
                            _logger.info("Henco Api: {}, Response Date: {}".format(prod_henco_ref,response_data.get('Shipments')))
                    else :
                        _logger.info(
                            "No response data found for Henco reference: {} ".format(prod_henco_ref))
            except Exception as e:
                _logger.error("Exception occurred: {}".format(e))
                return {'success': False,
                         'error_message': str(e)
                        }

    def data_of_henco_api(self,request_type, api_url, request_data, header):
            """
                Author: siddharth.vasani@setuconsulting.com
                Date: 30/01/25
                Task: Migration to v18 from v16
                Purpose: This method is called from the method : set_henco_api_data. It's used to check whether the response is 200 or not. If its 200 then
                        response_data will be send.
            """
            _logger.info("Henco API URL:::: %s" % api_url)
            _logger.info("Henco(body) Request Data:::: %s" % request_data)
            response_data = requests.request(method=request_type, url=api_url, headers=header, data=request_data)
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                _logger.info("Henco Response Data {}".format(response_data))
                return True, response_data
            else:
                _logger.info("Status Code :{} \n Henco Response Data {} \n Henco Api : {}".format(response_data.status_code,response_data,api_url))
                return False, response_data

    @api.model
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/02/25
            Task: Migration to v18 from v16
            Purpose: to set the records of the tab Arrival Dates History during create.
        """
        if vals.get('date_planned', False):
            convert_str_into_datetime = datetime.datetime.strptime(vals['date_planned'],
                                                                   '%Y-%m-%d %H:%M:%S') if vals.get(
                'date_planned') and type(vals.get('date_planned')) == str else vals['date_planned']
            vals['arrival_date_history_ids'] = [
                (0, 0, {'update_date': datetime.date.today(), 'last_arrival_date': convert_str_into_datetime})]
        return super(PurchaseOrder, self).create(vals)

    def copy(self, default=None):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/02/25
            Task: Migration to v18 from v16
            Purpose: to set the default expected date when order are copied.
        """
        default = dict(default or {})
        default['date_planned'] = self.date_planned
        return super(PurchaseOrder, self).copy(default)

