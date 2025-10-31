from odoo import api, fields, models
import logging
_logger = logging.getLogger("Recompute sale orders cost")


class SaleOrderCostChange(models.TransientModel):
    _name = 'sale.order.cost.change.wizard'
    _description = 'Change the product cost of selected saleorder'

    from_date = fields.Datetime(string="From")
    to_date = fields.Datetime(string="To")

    sale_order_ids = fields.Many2many('sale.order', string="Sale orders")

    @api.onchange('from_date', 'to_date')
    def onchange_method(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 05/12/24
            Task: Migration from V16 to V18
            Purpose: if from date and to date is set, then return sale order ids.
        """
        if self.from_date and self.to_date:
            sale_order_obj = self.env['sale.order']
            sale_orders = sale_order_obj.sudo().search(
                [('state', 'in', ['sale', 'done']), ('date_order', '>=', self.from_date),
                 ('date_order', '<=', self.to_date)])
            ids = sale_orders.ids
            self.sale_order_ids = [(6, 0, ids)]

    def change_product_cost(self):
        """
              Author: jay.garach@setuconsulting.com
              Date: 05/12/24
              Task: Migration from V16 to V18
              Purpose:set cost price in sale order line according to currency of sale order and company currency.
              With the configuration
              - Automatic Accounting
              - product -> category -> Inventory Valuation = Automatic
        """
        _logger.info("Total sale orders for this batch==>%s"%len(self.sale_order_ids.ids))
        sale_order_obj = self.env['sale.order']
        for count,so in enumerate(self.sale_order_ids.ids,start=1):
            so = sale_order_obj.browse(so)
            print("Sale_order:-", so.name)
            for line in so.order_line.read_group(groupby=['product_id'], fields=[], domain=[('order_id', '=', so.id),('product_id','!=',False)]):
                # flag_divide = True
                product_id = self.env['product.product'].browse(line.get('product_id')[0])
                bom = self.env['mrp.bom']._bom_find(products=product_id, company_id=self.env.user.company_id.id).get(product_id)
                sale_order_lines = so.order_line.filtered(lambda sol: sol.product_id.id == product_id.id)
                if bom and bom.type == 'phantom':
                    product_id = bom.bom_line_ids.mapped('product_id')
                s_moves = so.picking_ids.filtered(lambda sp: sp.state == 'done').mapped('move_ids').filtered(
                    lambda mv: mv.product_id.id in product_id.ids and mv.state == 'done')
                if not s_moves:
                    s_moves = self.env['stock.move'].search([('picking_id', 'in', so.picking_ids.ids),
                                                             ('sale_line_id', 'in', sale_order_lines.ids), ('state', '=', 'done')])
                    # flag_divide = False
                a_moves = self.env['account.move'].search([('stock_move_id', 'in', s_moves.ids)])
                if a_moves and line.get('qty_delivered'):
                    sale_amount = sum(a_moves.filtered(lambda move:move.stock_move_id.picking_id.picking_type_id.code == 'outgoing').mapped('amount_total'))
                    sale_return_amount = sum(a_moves.filtered(lambda move:move.stock_move_id.picking_id.picking_type_id.code == 'incoming').mapped('amount_total')) or 0
                    purchase_price = (sale_amount - sale_return_amount) / line.get('qty_delivered')
                    for sol in sale_order_lines:
                        sol.purchase_price_base = purchase_price
                    if so.currency_id.id != self.env.user.company_id.currency_id.id:
                        purchase_price = self.env.user.company_id.currency_id._convert(
                            purchase_price, so.currency_id, self.env.user.company_id, a_moves.mapped('date')[-1])
                    for sol in sale_order_lines:
                        sol.purchase_price = purchase_price
                        sol._compute_margin()
                        if sol.invoice_lines:
                            self._cr.execute(f"""update  account_move_line 
                                                 set purchase_price = sol.purchase_price,
                                                 purchase_price_base = sol.purchase_price_base 
                                                 from sale_order_line sol 
                                                 join sale_order_line_invoice_rel cp on cp.order_line_id = sol.id 
                                                 where  cp.invoice_line_id = account_move_line.id and sol.id = {sol.id}""")


            if count%100 ==0:
                self._cr.commit()
            _logger.info(f"Processed Sale order:=>{so.name},so_id:=>{so.id} ,Date order:=>{so.date_order} , {count} out of {len(self.sale_order_ids.ids)}")