# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    country_ids = fields.Many2many(
        comodel_name="res.country",
        relation="product_temp_country_rel",
        column1="product_temp_id",
        column2="country_id", string="Countries")

    def search(self, domain, offset=0, limit=None, order=None):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 16-01-2025
        Task: [1478] Product Catalog per country
        Purpose: This method will sort the products ABC classification wise and then as per net on hand.
        :param args: Searching argument.
        :param offset: Offset.
        :param limit: Dataset limit.
        :param order: Order or sequence.
        :param count: Count.
        :return: Product template objects.
        """
        res = super(ProductTemplate, self).search(domain=domain, offset=offset, limit=limit, order=order)
        if self._context.get('bin_size', False) and self._context.get('from_product_loading_page', False):
            order_by_list = ['list_price desc', 'list_price asc', 'name asc', 'name desc']
            warehouses = self.env['stock.warehouse'].sudo().search([])
            order_acco_abc = False
            if order:
                for order_name in order_by_list:
                    if order_name in order.split(','):
                        order_acco_abc = True
            warehouse_str = ""
            product_str = ""
            if warehouses:
                warehouse_str = """and source_ware.id in (%s)""" % (",".join(map(str, warehouses.ids)))
            if res:
                if order and not order_acco_abc:
                    if res.ids:
                        product_str = """and pt.id in (%s)""" % (",".join(map(str, res.ids)))
                    else:
                        product_str = ""
                    query = """
                        with all_data as (
                            select  
                                    d.product as product, 
                                    d.value as value, 
                                    d.net_on_hand as net_on_hand, 
                                    rank, 
                                    p_type,
                                    published
                            from (
                                    select d.product as product, 
                                    d.value_text as value, 
                                    sum(d.net_on_hand) over(partition by d.product) as net_on_hand,
                                           row_number() over(partition by d.product order by --sum(d.net_on_hand),
                                                             d.p_type asc, d.value_text asc) as rank,
                                            d.p_type as p_type,d.published as published
                                        from (
                                                select 
                                                    pt.is_published as published,
                                                    case
                                                        when pp.abc_classification = 'C' then 3 else
                                                        case when pp.abc_classification = 'B' then 2 else
                                                        case when pp.abc_classification = 'A' then 1 else
                                                        4 end end
                                                    end as
                                                     value_text,
                                                     pt.product_type_marvelsa as type,
                                                     pt.id as product,
                                                     0 as net_on_hand,
                                                     case
                                                        when pt.product_type_marvelsa = '3' then 3 else
                                                        case when pt.product_type_marvelsa = '2' then 2 else
                                                        case when pt.product_type_marvelsa = '1' then 1 else
                                                        case when pt.product_type_marvelsa = '4' then 4 else
                                                    5 end end end
                                                    end as p_type
                
                                                 from
                                                    product_product pp
                                                        left Join  product_template pt on pt.id = pp.product_tmpl_id
                                                        --left Join ir_property ip on ip.name = 'abc_classification' and ip.res_id = 'product.product,' || pp.id
                                                    where pt.active='t' 
                                                        and pt.sale_ok='t' {product_str}
                                                    group by pt.product_type_marvelsa, pp.abc_classification, pt.id,pt.is_published
                
                                                Union All
                
                                                select pt.is_published as published,
                                                    case
                                                        when pp.abc_classification = 'C' then 3 else
                                                        case when pp.abc_classification = 'B' then 2 else
                                                        case when pp.abc_classification = 'A' then 1 else
                                                        4 end end
                                                    end as
                                                     value_text,pt.product_type_marvelsa as type,pt.id as product,sum(sq.quantity - sq.reserved_quantity) as net_on_hand,
                                                     case
                                                        when pt.product_type_marvelsa = '3' then 3 else
                                                        case when pt.product_type_marvelsa = '2' then 2 else
                                                        case when pt.product_type_marvelsa = '1' then 1 else
                                                        case when pt.product_type_marvelsa = '4' then 4 else
                                                        5 end end end
                                                    end as p_type
                
                                                 from
                                                    product_product pp
                                                    Left Join product_template pt on pt.id = pp.product_tmpl_id
                                                        left join stock_quant sq on pp.id = sq.product_id
                                                        left join stock_location loc on loc.id = sq.location_id
                                                        Left Join stock_warehouse source_ware ON loc.parent_path::text ~~ concat('%/', source_ware.view_location_id, '/%')
                                                        --Left Join ir_property ip on ip.name = 'abc_classification' and ip.res_id = 'product.product,' || pp.id
                                                    --and ip.company_id = sq.company_id
                                                    where loc.usage = 'internal'
                                                    and  pt.active='t' and pt.sale_ok='t' {warehouse_str} {product_str}
                                                    group by  pt.product_type_marvelsa, pp.abc_classification, pt.id ,pt.is_published
                                        )d
                                        group by d.product, d.p_type, d.value_text, d.net_on_hand,d.published
                                        order by published desc,d.p_type asc , d.value_text asc--, d.net_on_hand desc, d.product
                
                                    )d where rank=1 
                                    order by published desc ,d.p_type asc, d.value asc --, d.net_on_hand desc, d.product
                                    )
                
                                    select * from all_data ;""".format(
                        warehouse_str=warehouse_str, product_str=product_str)
                    self._cr.execute(query)
                    result = self._cr.fetchall()
                    result = result and len(result[0]) > 1 and [rec[0] for rec in result] or []
                    Product = self.env['product.template'].sudo().with_context(bin_size=True)
                    res = Product.browse(result)
        return res
