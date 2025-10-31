from odoo import fields, models, api, _
from datetime import timedelta
from odoo.exceptions import ValidationError


class SalesTimeDashboard(models.TransientModel):
    _name = 'sales.time.dashboard'
    _description = "SalesTimeDashboard"

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End date')

    leave_dates = []
    avg_hours = 0

    is_created_from_website = fields.Char(string='Website Origin')
    so_name = fields.Many2one('sale.order', string='Sales Order')
    # create_sale_order_date = fields.Datetime(related='so_name.date_order', store=True)
    create_sale_order_date = fields.Datetime(string='Create Sale Order Date')
    created_user_id = fields.Many2one('res.users', string='Created by User')
    picking_name = fields.Many2one('stock.picking', string='Delivery Order')

    actual_hours_to_confirm_so = fields.Float(string='Confirmation', group_operator="avg")
    # hours_to_confirm_so = fields.Float(string='Total Confirmation')

    actual_hours_to_confirm_so_by_customer = fields.Float(string='Customer Confirmation', group_operator="avg")
    # hours_to_confirm_so_by_customer = fields.Float(string='customer Confirmation')

    actual_hours_to_create_picking = fields.Float(string='Picking', group_operator="avg")
    # hours_to_create_picking = fields.Float(string='Total Picking')

    actual_hours_to_create_invoice = fields.Float(string='Invoicing', group_operator="avg")
    # hours_to_create_invoice = fields.Float(string='Total Invoicing')

    actual_hours_to_prepare_picking = fields.Float(string='Shipping (Preparation)', group_operator="avg")
    # hours_to_prepare_picking = fields.Float(string='Total Shipping (Preparation)')

    actual_hours_to_delivery = fields.Float(string='Delivered (Wait)', group_operator="avg")
    # hours_to_delivery = fields.Float(string='Total Delivered (Wait)')

    actual_total_time_taken = fields.Float(string='Total', group_operator="avg")
    # total_time_taken = fields.Float(string='Overall Total')

    actual_hours_to_send_order = fields.Float(string='Order Sent', group_operator="avg")
    wizard_id = fields.Integer()
    cliente_mostrador = fields.Boolean('Cliente Mostrador')
    partner_id = fields.Many2one('res.partner', 'Customer')
    team_id = fields.Many2one('crm.team', 'Sale Team')
    detener_envio = fields.Boolean('Detener envio')
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier')
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    payment_status = fields.Char(string='Payment Status')
    payment_state = fields.Char(string='Payment State')
    date_order_received = fields.Datetime(string='Date Order Received')
    preparation_date = fields.Datetime(string='Preparation Date')
    x_studio_fecha_de_envio = fields.Datetime(string='Fecha de Envio')
    x_studio_fecha_de_entrega = fields.Datetime(string='X Studio Fecha De Entrega')
    carrier_tracking_ref = fields.Char(string='Tracking Reference')
    delivery_cost = fields.Float(string='Delivery cost')

    # min_time = datetime.min.time()

    def get_sales_time_report(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To open sales time dashboard wizard
        """
        shift = self.env['resource.calendar'].search([('use_for_sales_time_report', '=', True)])
        if not shift:
            raise ValidationError("Please select default work shift for calculating data.")

        tree_view_id = self.env.ref('setu_sales_time_dashboard.sales_time_dashboard_tree').id
        viewmode = "list"
        self.get_data()
        return {
            'name': _('Sales Time Report from %s to %s') % (self.start_date, self.end_date),
            'res_model': 'sales.time.dashboard',
            'domain': [('wizard_id', '=', self.id)],
            'view_mode': viewmode,
            'type': 'ir.actions.act_window',
            'view': tree_view_id,
            'help': """
                        <p class="o_view_nocontent_smiling_face">
                            No data found.
                        </p>
                    """,
        }

    def get_data(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To get data from query function (get_sales_time_data(start_date,end_date) location -- get_sales_time_data.sql file)
            --> currently insert from sql side and removed from set it from python side as it takes much time from here so commented below code to create vals..
        """
        end_date = self.end_date + timedelta(days=1)
        query = """select * from get_sales_time_data('%s', '%s', '%d')""" % (self.start_date, end_date, self.id)
        self._cr.execute(query)
        # data = self._cr.dictfetchall()
        # for line in data:
        #     actual_hours_to_confirm_so = line.get('actual_hours_to_confirm_so', 0)
        #     actual_hours_to_confirm_so_by_customer = line.get('actual_hours_to_confirm_so_by_customer',0)
        #     actual_hours_to_create_picking = line.get('actual_hours_to_create_picking', 0)
        #     actual_hours_to_create_invoice = line.get('actual_hours_to_create_invoice', 0)
        #     actual_hours_to_prepare_picking = line.get('actual_hours_to_prepare_picking', 0)
        #     actual_hours_to_delivery = line.get('actual_hours_to_delivery', 0)
        #     actual_total_time_taken = line.get('actual_total_time_taken', 0)
        #     actual_hours_to_send_order = line.get('actual_hours_to_send_order', 0)
        #     cliente_mostrador = line.get('cliente_mostrador')
        #     partner_id = line.get('partner_id')
        #     team_id = line.get('team_id')
        #     detener_envio = line.get('dfactura')
        #     carrier_id = line.get('carrier_id')
        #     payment_term_id = line.get('payment_term_id')
        #     payment_status = line.get('payment_status')
        #     payment_state = line.get('payment_state')
        #     date_order_received = line.get('date_order_received')
        #     preparation_date = line.get('preparation_date')
        #     x_studio_fecha_de_envio = line.get('x_studio_fecha_de_envio')
        #     x_studio_fecha_de_entrega = line.get('x_studio_fecha_de_entrega')
        #     carrier_tracking_ref = line.get('carrier_tracking_ref')
        #     delivery_cost = line.get('delivery_cost')
        #
        #
        #
        #     if actual_hours_to_confirm_so == 0 and actual_hours_to_create_picking == 0 and actual_hours_to_create_invoice == 0 \
        #             and actual_hours_to_prepare_picking == 0 and actual_hours_to_delivery == 0 and actual_total_time_taken == 0 and actual_hours_to_send_order==0:
        #         continue
        #     order_id = line.get('order_id')
        #     vals = {
        #         'wizard_id': self.id,
        #         'so_name': line.get('order_id'),
        #         'picking_name': line.get('picking_id'),
        #         'is_created_from_website': line.get('website'),
        #         'actual_hours_to_confirm_so': actual_hours_to_confirm_so,
        #         'actual_hours_to_confirm_so_by_customer': actual_hours_to_confirm_so_by_customer,
        #         'actual_hours_to_create_picking': actual_hours_to_create_picking,
        #         'actual_hours_to_create_invoice': actual_hours_to_create_invoice,
        #         'actual_hours_to_prepare_picking': actual_hours_to_prepare_picking,
        #         'actual_hours_to_delivery': actual_hours_to_delivery,
        #         'actual_hours_to_send_order': actual_hours_to_send_order,
        #         'actual_total_time_taken': actual_total_time_taken,
        #         'cliente_mostrador': cliente_mostrador,
        #         'partner_id': partner_id,
        #         'team_id': team_id,
        #         'detener_envio':detener_envio,
        #         'carrier_id': carrier_id,
        #         'payment_term_id': payment_term_id,
        #         'payment_status': payment_status,
        #         'payment_state': payment_state,
        #         'date_order_received': date_order_received,
        #         'preparation_date': preparation_date,
        #         'x_studio_fecha_de_envio': x_studio_fecha_de_envio,
        #         'x_studio_fecha_de_entrega': x_studio_fecha_de_entrega,
        #         'carrier_tracking_ref': carrier_tracking_ref,
        #         'delivery_cost': delivery_cost
        #     }
        #     self.create(vals)
        return True
