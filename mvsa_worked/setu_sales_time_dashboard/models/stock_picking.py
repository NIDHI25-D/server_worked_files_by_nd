from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_studio_fecha_de_entrega = fields.Datetime(copy=False)
    confirm_date_done_diff = fields.Float(string='Picking Duration', default=0, copy=False)
    date_done_date_invoice_diff = fields.Float(string='Invoicing Duration', default=0, copy=False)
    date_invoice_preparation_date_diff = fields.Float(string='Shipping (Preparation) Duration', default=0, copy=False)
    preparation_date_shipping_date_diff = fields.Float(string='Shipping (Wait) Duration', default=0, copy=False)
    preparation_date = fields.Datetime(string="Preparation Date",copy=False)
    x_studio_fecha_de_envio = fields.Datetime(string="Shipping Date", copy=False)
    shipping_date_delivery_date_diff = fields.Float(string='Order Sent', default=0, copy=False)
    date_order_received = fields.Datetime(string='Date Order Received',copy=False)
    is_cancellation_invoice = fields.Boolean(string="Is Cancellation Invoice")

    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     """
    #         Author: smith@setuconsulting
    #         Date: 05/05/23
    #         Task: Migration
    #         Purpose: this method set current date while duplicating picking
    #     """
    #
    #     self.ensure_one()
    #     order = super().copy(default=default)
    #     if self.preparation_date:
    #         order.preparation_date = datetime.now()
    #     return orderX

    @api.onchange('preparation_date', 'x_studio_fecha_de_envio', 'x_studio_fecha_de_entrega', 'date_done')
    def onchange_preparation_and_shipped_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: (1) date_invoice_preparation_date_diff (Shipping (Preparation) Duration) is calculated time duration between picking done date and picking preparation date.
                     (2) preparation_date_shipping_date_diff (Shipping (Wait) Duration) is calculated time duration between picking preparation date and picking shipping date.
                     (3) shipping_date_delivery_date_diff (Order Sent) is calculated time duration between picking shipping date and picking x_studio_fecha_de_entrega date field.
        """

        resource_obj = self.env['resource.calendar'].sudo()
        for record in self:
            if record.picking_type_id.code == 'outgoing':
                sale_id = record.sale_id or False
                preparation_date = record.preparation_date
                x_studio_fecha_de_envio = record.x_studio_fecha_de_envio
                x_studio_fecha_de_entrega = record.x_studio_fecha_de_entrega
                picking_date_done = record.date_done
                if preparation_date and picking_date_done:
                    record.date_invoice_preparation_date_diff = resource_obj.get_shift_wise_hours(picking_date_done,
                                                                                                  preparation_date)
                if x_studio_fecha_de_envio and preparation_date:
                    record.preparation_date_shipping_date_diff = resource_obj.get_shift_wise_hours(
                        preparation_date, x_studio_fecha_de_envio)

                if x_studio_fecha_de_envio and x_studio_fecha_de_entrega:
                    record.shipping_date_delivery_date_diff = resource_obj.get_shift_wise_hours(x_studio_fecha_de_envio,
                                                                                                x_studio_fecha_de_entrega)

    def _action_done(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: To calculate confirm_date_done_diff (picking duration) (picking done date and sale order confirmation date)
        """

        res = super(StockPicking, self)._action_done()
        resource_obj = self.env['resource.calendar'].sudo()
        for record in self:
            if record.picking_type_id and record.picking_type_id.code != 'outgoing':
                continue
            # confirmation_date = record.sale_id and record.sale_id.date_order or False
            confirmation_date = record.scheduled_date
            date_done = record.date_done
            preparation_date = record.preparation_date
            shipping_date = record.x_studio_fecha_de_envio
            picking_update_vals = {}
            if confirmation_date and date_done:
                confirm_date_done_diff = resource_obj.get_shift_wise_hours(confirmation_date, date_done)
                picking_update_vals.update({'confirm_date_done_diff': confirm_date_done_diff})
            if picking_update_vals:
                record.write(picking_update_vals)
        return res

    @api.constrains('preparation_date', 'x_studio_fecha_de_envio', 'x_studio_fecha_de_entrega', 'date_order_received')
    def date_constrains(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 26/12/24
            Task: Migration to v18 from v16
            Purpose: Raise error as per the conditions
        """
        for record in self:
            if record.preparation_date and record.date_order_received and record.preparation_date <= record.date_order_received:
                raise ValidationError(_('Preparation date is lower than Date Order Received'))
            if record.x_studio_fecha_de_envio and record.preparation_date and record.x_studio_fecha_de_envio <= record.preparation_date:
                raise ValidationError(_('Fecha De Envio is lower than Preparation date'))
            if record.x_studio_fecha_de_envio and record.x_studio_fecha_de_entrega and record.x_studio_fecha_de_entrega <= record.x_studio_fecha_de_envio:
                raise ValidationError(_('X Studio Fecha De Entrega is lower than Fecha De Envio '))
