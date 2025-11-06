from odoo import models, fields, api, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    hr_employee_id = fields.Many2one('hr.employee', string="Technical Person")
    repair_state_ctb_id = fields.Many2one('repair.state.ctb', string="State Order CTB", domain=[('active', '=', True)],
                                           tracking=True) #,group_expand='_read_group_stage_ids'
    repair_state_ctb_history_ids = fields.One2many('repair.state.ctb.history', 'repair_order_id',
                                                   string="History State CTB", tracking=True)
    invoice_method = fields.Selection([
        ("none", "No Invoice"),
        ("b4repair", "Before Repair"),
        ("after_repair", "After Repair")], string="Invoice Method",
        default='after_repair', index=True, readonly=True, required=True, tracking=True,
        states={'draft': [('readonly', False)]},
        help='Selecting \'Before Repair\' or \'After Repair\' will allow you to generate invoice before or after the repair is done respectively. \'No invoice\' means you don\'t want to generate invoice for this repair order.')

    model = fields.Char('Contact Information')
    serial_number = fields.Char('Serial Number')
    reported_failure = fields.Text('Reported Failure')
    date_fecha = fields.Datetime(string='Date Delivery')
    client_signature = fields.Binary(string="Client's Signature")
    employee_id = fields.Many2one('hr.employee', string='Delivers')
    receive_partner_id = fields.Many2one('res.partner', string='Receives')
    telephone = fields.Char(related='partner_id.phone')
    tag_id = fields.Many2one('repair.tags')

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     return self.env['repair.state.ctb'].search([], order=order)

    # @api.model
    # def create(self, vals):
    #     if vals.get('repair_state_ctb_id', False):
    #         vals['repair_state_ctb_history_ids'] = [(0, 0, {'repair_state_ctb_id': vals['repair_state_ctb_id']})]
    #
    #     return super(RepairOrder, self).create(vals)

    # def write(self, values):
    #     if values.get('repair_state_ctb_id', False):
    #         values['repair_state_ctb_history_ids'] = [(0, 0, {'repair_state_ctb_id': values['repair_state_ctb_id']})]
    #
    #     return super(RepairOrder, self).write(values)

    # @api.model
    # def create(self, vals):
    #     res = super(RepairOrder, self).create(vals)
    #     if vals.get('invoice_method') != "after_repair":
    #         res.message_post(body=_("Invoice Method: <b>After Repair -> %s</b>",
    #                                 dict(self._fields['invoice_method'].selection).get(vals.get('invoice_method'))))
    #     return res

    # def update_price_for_repair_order(self):
    #     if self.operations and self.pricelist_id:
    #         self.ensure_one()
    #         lines_to_update = []
    #         for line in self.operations.filtered(lambda x: x.type == 'add'):
    #             product = line.product_id.with_context(
    #                 type=line.type,
    #                 quantity=line.product_uom_qty,
    #                 pricelist=self.pricelist_id.id,
    #             )
    #             price_unit_for_products = self.env['product.pricelist'].browse(
    #                 self.pricelist_id.id)._compute_price_rule(product, line.product_uom_qty, uom_id=line.product_id.uom_id.id, date=False)
    #             lines_to_update.append((1, line.id, {'price_unit': price_unit_for_products.get(product.id)[0]}))
    #         self.update({'operations': lines_to_update})

    # def action_repair_cancel(self):
    #     if self.state in ('done', '2binvoiced') and not self.invoiced:
    #         moves = self.env['stock.move'].search([('repair_id', '=', self.id), ('state', '=', 'done')],
    #                                               limit=len(self.operations.mapped('product_id').ids) + 1,
    #                                               order='create_date desc')
    #         for move in moves:
    #             new_move = move.copy({'state': 'draft', 'location_id': move.location_dest_id.id,
    #                                   'location_dest_id': move.location_id.id})
    #             new_move._action_confirm()
    #             new_move._set_quantity_done(move.product_uom_qty)
    #             new_move._action_done()
    #     return super(RepairOrder, self).action_repair_cancel()

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     super().onchange_partner_id()
    #     self = self.with_company(self.company_id)
    #     if not self.partner_id:
    #         change_pricelist_id = self.env['ir.default'].sudo().get('res.config.settings', 'change_pricelist_id')
    #         if change_pricelist_id:
    #             self.pricelist_id = change_pricelist_id
