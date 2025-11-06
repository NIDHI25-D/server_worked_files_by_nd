from odoo import models, fields, api
from odoo.tools import SQL, sql


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    purchase_product_cost = fields.Float('Product Cost')
    purchase_product_cost_base_currency = fields.Float('Product cost (Base currency)')
    sale_margin = fields.Float('Margin')

    @property
    def _table_query(self):
        return SQL("""SELECT S.*,s.product_cost * s.quantity as purchase_product_cost,
        s.product_sale_margin - s.purchase_product_cost_currency * s.quantity as sale_margin,
        s.purchase_product_cost_currency * s.quantity as purchase_product_cost_base_currency FROM (%s) S
        """, super()._table_query)

    def _select(self):
        return SQL(
            """%s,COALESCE(line.purchase_price,0) as product_cost,line.balance * account_currency_table.rate
            as product_sale_margin,COALESCE(line.purchase_price_base,0) as purchase_product_cost_currency""",
            super(AccountInvoiceReport, self)._select())
