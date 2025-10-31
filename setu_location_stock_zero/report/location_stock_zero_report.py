
from odoo import fields, models
from odoo import tools


class LocationStockZero(models.Model):
    _name = 'location.stock.zero.report'
    _auto = False
    _description = 'Location Stock Zero'

    name = fields.Char(string="Warehouse")
    location = fields.Char(string="Location Stock")

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        """
            Author: siddharth.vasani@setuconsulting.com
            Task: Migration to v18 from v16
            Purpose: execute the query to create report for zero stock.
        """
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            row_number() over() as id,
            
            sw.name as name,
            sd.complete_name as location

        """

        for field in fields.values():
            select_ += field

        from_ = """
                 stock_warehouse sw
	                    Left join stock_location sl on(sw.lot_stock_id = sl.id)
	                    join stock_location sd on (sl.id =sd.location_id)
	                    Left join stock_quant sq on (sd.id = sq.location_id)
                %s
        """ % from_clause

        groupby_ = """
            sw.name,
            sl.complete_name,
            sd.complete_name %s
        """ % (groupby)

        return """%s (SELECT %s FROM %s  WHERE sl.usage='internal' and sd.active and sw.active GROUP BY %s having coalesce(sum(sq.quantity),0::double precision)<=0)""" % (
            with_, select_, from_, groupby_)

    def init(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Task: Migration to v18 from v16
            Purpose: called init to execute the query.
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
