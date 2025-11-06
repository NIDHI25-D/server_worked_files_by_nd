# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    setu_generic_product_image_ids = fields.One2many(
        comodel_name="setu.generic.product.image",
        inverse_name="product_id", string='Product Images')
    is_drop_ship_product = fields.Boolean(
        string="Is Drop Ship Product?", store=False,
        compute="_compute_is_drop_ship_product")

    @api.depends('route_ids')
    def _compute_is_drop_ship_product(self):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : compute product is drop-ship product based on route
        :return: None
        """
        stock_rule_obj = self.env['stock.rule']
        stock_location_obj = self.env['stock.location']
        customer_locations = stock_location_obj.search([('usage', '=', 'customer')])
        route_ids = self.route_ids | self.categ_id.route_ids
        stock_rule_id = stock_rule_obj.search([
            ('company_id', '=', self.env.user.company_id.id), ('action', '=', 'buy'),
            ('location_dest_id', 'in', customer_locations.ids),
            ('route_id', 'in', route_ids.ids)])
        if stock_rule_id:
            self.is_drop_ship_product = True
        else:
            self.is_drop_ship_product = False

    def find_product_free_qty_stock(self, warehouse, product_list):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for find free stock qty
        :param warehouse:
        :param product_list:
        :return: dictionary with product and qty
        """
        qty_on_hand = {}
        location_ids, product_ids = self.get_locations_and_product(warehouse, product_list)

        bom_product_ids = self.get_bom_product_lst(product_ids)
        if bom_product_ids:
            bom_products = self.with_context(warehouse=warehouse.ids).browse(bom_product_ids)
            for product in bom_products:
                actual_stock = getattr(product, 'free_qty')
                qty_on_hand.update({product.id: actual_stock})

        simple_product_list = list(set(product_list) - set(bom_product_ids))
        simple_product_list_ids = ','.join(str(pre) for pre in simple_product_list)
        if simple_product_list_ids:
            qry = self.prepare_free_qty_query(location_ids, simple_product_list_ids)
            self._cr.execute(qry)
            result = self._cr.dictfetchall()
            for res in result:
                qty_on_hand.update({res.get('product_id'): res.get('stock')})
        return qty_on_hand

    def find_product_forecast_stock(self, warehouse, product_list):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for find product forecasted qty stock
        :param warehouse:
        :param product_list:
        :return: dictionary with product and qty
        """
        forecasted_qty = {}
        location_ids, product_ids = self.get_locations_and_product(warehouse, product_list)

        bom_product_ids = self.get_bom_product_lst(product_ids)
        if bom_product_ids:
            bom_products = self.with_context(warehouse=warehouse.ids).browse(bom_product_ids)
            for product in bom_products:
                actual_stock = getattr(product, 'free_qty') + getattr(product, 'incoming_qty')
                forecasted_qty.update({product.id: actual_stock})

        simple_product_list = list(set(product_list) - set(bom_product_ids))
        simple_product_list_ids = ','.join(str(e) for e in simple_product_list)
        if simple_product_list_ids:
            qry = self.prepare_forecasted_qty_query(location_ids, simple_product_list_ids)
            self._cr.execute(qry)
            result = self._cr.dictfetchall()
            for i in result:
                forecasted_qty.update({i.get('product_id'): i.get('stock')})
        return forecasted_qty

    def get_locations_and_product(self, warehouse, product_list):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for get locations and products ids
        :param warehouse:
        :param product_list:
        :return: location_ids, products_ids
        """
        locations = self.env['stock.location'].search([('location_id', 'child_of', warehouse.lot_stock_id.ids)])
        location_ids = ','.join(str(e) for e in locations.ids)
        product_ids = ','.join(str(e) for e in product_list)
        return location_ids, product_ids

    def prepare_free_qty_query(self, location_ids, simple_product_list_ids):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use to prepare query for free qty
        :param location_ids:
        :param simple_product_list_ids:
        :return: query
        """
        query = """select pp.id as product_id, COALESCE(sum(sq.quantity)-sum(sq.reserved_quantity),0) as stock from 
        product_product pp  left join stock_quant sq on pp.id = sq.product_id and sq.location_id in (%s)  where pp.id 
        in (%s) group by pp.id""" % (
            location_ids, simple_product_list_ids)
        return query

    def prepare_forecasted_qty_query(self, location_ids, simple_product_list_ids):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use to prepare query for forecasted qty
        :param location_ids:
        :param simple_product_list_ids:
        :return: query
        """
        query = ("""select * from (select pp.id as product_id,  COALESCE(sum(sq.quantity)-sum(sq.reserved_quantity),0) as stock
                    from product_product pp  left join stock_quant sq on pp.id = sq.product_id and sq.location_id in (%s)  where pp.id in (%s) group by pp.id
                    union all  select product_id as product_id, sum(product_qty) as stock from stock_move where state in ('assigned') and product_id in (%s) and location_dest_id in (%s)
                    group by product_id) as product_info""" % (
            location_ids, simple_product_list_ids, simple_product_list_ids, location_ids))
        return query

    def product_stock_movement(self, from_datetime, company=False):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use find product created stock movement
        :param from_datetime:
        :param company:
        :return: list
        """
        result = []
        module_obj = self.env['ir.module.module']
        mrp_module = module_obj.sudo().search([('name', '=', 'mrp'), ('state', '=', 'installed')])
        date = str(datetime.strftime(from_datetime, '%Y-%m-%d %H:%M:%S'))

        if mrp_module:
            mrp_qry = ("""select p.id as product_id from product_product as p
                    inner join mrp_bom as mb on mb.product_tmpl_id=p.product_tmpl_id
                    inner join mrp_bom_line as ml on ml.bom_id=mb.id
                    inner join stock_move as sm on sm.product_id=ml.product_id
                    where sm.date >= '%s' and sm.company_id = %d and sm.state in 
                    ('partially_available','assigned','done')""" % (date, company.id))
            self._cr.execute(mrp_qry)
            result = self._cr.dictfetchall()
        qry = (
                """select product_id from stock_move where date >= '%s' and  state in ('partially_available','assigned','done')""" % (
            date))
        if company:
            qry += ("""and company_id = %d""" % company.id)

        self._cr.execute(qry)
        result += self._cr.dictfetchall()
        product_ids = [product_id.get('product_id') for product_id in result]

        return list(set(product_ids))

    def prepare_generic_image_vals(self, vals):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for prepare generic image vals
        :param vals:
        :return: dictionary
        """
        vals = {"sequence": 0,
                "image": vals.get("image_1920", False),
                "name": self.name,
                "product_id": self.id,
                "template_id": self.product_tmpl_id.id}
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for create generic product image record
        :param vals_list:
        :return: recordset
        """
        setu_generic_product_image_obj = self.env['setu.generic.product.image']
        res_ids = super(ProductProduct, self).create(vals_list)
        for res_id, vals in zip(res_ids, vals_list):
            if vals.get("image_1920", False) and res_id:
                img_vals = res_id.prepare_generic_image_vals(vals)
                setu_generic_product_image_obj.create(img_vals)
        return res_ids

    def write(self, vals):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use for create generic product image record when changes image
        :param vals:
        :return: Ture or False
        """
        setu_generic_product_image_obj = self.env['setu.generic.product.image']
        res = super(ProductProduct, self).write(vals)
        if vals.get("image_1920", False) and self:
            for record in self:
                if vals.get("image_1920"):
                    img_vals = record.prepare_generic_image_vals(vals)
                    setu_generic_product_image_obj.create(img_vals)
        return res

    def get_bom_product_lst(self, product_ids):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use to find bom type product
        :param product_ids:
        :return: list
        """
        bom_product_ids = []
        module_obj = self.env['ir.module.module']

        mrp_module = module_obj.sudo().search([('name', '=', 'mrp'), ('state', '=', 'installed')])
        if mrp_module:
            qry = ("""select p.id as product_id from product_product as p inner join mrp_bom as mb on 
            mb.product_tmpl_id=p.product_tmpl_id  and p.id in (%s)""" % product_ids)
            self._cr.execute(qry)
            bom_product_ids = self._cr.dictfetchall()
            bom_product_ids = [product_id.get('product_id') for product_id in bom_product_ids]
        return bom_product_ids

    def search_and_set_odoo_product_default_code_barcode(self, template_attribute_value_ids, variation,
                                                         product_template):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use to set default code and barcode in odoo product
        :param template_attribute_value_ids:
        :param variation:
        :param product_template:
        :return: odoo product
        """
        sku = variation.get("sku")
        barcode = variation.get("barcode") or False
        if barcode and barcode.__eq__("false"):
            barcode = False
        odoo_product_id = False

        domain = []
        for template_attribute_value_id in template_attribute_value_ids:
            product_temp_vals_tuple = ("product_template_attribute_value_ids", "=", template_attribute_value_id)
            domain.append(product_temp_vals_tuple)

        domain and domain.append(("product_tmpl_id", "=", product_template.id))
        if domain:
            odoo_product_id = self.search(domain)
        if odoo_product_id and sku:
            odoo_product_id.write({"default_code": sku})
        if barcode and odoo_product_id:
            odoo_product_id.write({"barcode": barcode})

        return odoo_product_id

    def find_import_export_product_stock_field(self, multi_ecommerce_connector_id, product_ids, warehouse):
        """
        @name : Kamlesh Singh
        @date : 24/10/2024
        @purpose : This method will use to return free qty or forecast qty
        :param multi_ecommerce_connector_id:
        :param product_ids:
        :param warehouse:
        :return: dictionary
        """
        product_stock = {}
        if product_ids:
            if multi_ecommerce_connector_id.stock_field_id.name == "free_qty":
                product_stock = self.find_product_free_qty_stock(warehouse, product_ids)
            elif multi_ecommerce_connector_id.stock_field_id.name == "virtual_available":
                product_stock = self.find_product_forecast_stock(warehouse, product_ids)
        return product_stock
