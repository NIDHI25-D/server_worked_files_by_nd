from odoo import fields, models, api


class SaleReport(models.Model):
    _inherit = 'sale.report'

    is_urgent_order = fields.Boolean(string="Urgent Order")

    def _select_sale(self):
        res = super(SaleReport, self)._select_sale()
        res = '%s,s.is_urgent_order AS is_urgent_order' % res
        return res

    def _group_by_sale(self):
        res = super(SaleReport, self)._group_by_sale()
        res += """,
            s.is_urgent_order"""
        return res

    def _select_pos(self):
        res = super(SaleReport, self)._select_pos()
        res = '%s,NULL as is_urgent_order' % res
        return res

    def _group_by_pos(self):
        res = super(SaleReport, self)._group_by_pos()
        res += """,
                is_urgent_order"""
        return res
