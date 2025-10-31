from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_view_opportunity_count = fields.Integer("Opportunity Count",
                                                    compute='_compute_contact_view_opportunity_count', store=True)
    contact_view_sale_count = fields.Integer("Sale Order Count", compute='_compute_contact_view_sale_count', store=True)
    contact_view_purchase_count = fields.Integer("Purchase Order Count", compute='_compute_contact_view_purchase_count',
                                                 store=True)
    contact_view_total_invoice = fields.Monetary("Invoice Total", compute='_compute_contact_view_invoice_amount',
                                                 store=True)
    contact_view_supplier_invoice_count = fields.Integer("Supplier Invoice Count",
                                                         compute='_compute_contact_view_supplier_invoice_count',
                                                         store=True)

    contact_view_property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', compute='_compute_contact_view_product_pricelist', store=True
    )

    @api.depends('parent_id', 'child_ids', 'child_ids.opportunity_ids','child_ids.opportunity_ids.stage_id', 'opportunity_ids', 'opportunity_ids.stage_id','parent_id.opportunity_ids',
                 'opportunity_ids.active', 'parent_id.opportunity_ids.active','parent_id.opportunity_ids.stage_id')
    def _compute_contact_view_opportunity_count(self):
        for rec in self:
            is_delete = False
            mod_qty = abs(rec.contact_view_opportunity_count - rec.opportunity_count)
            if rec.contact_view_opportunity_count > rec.opportunity_count:
                is_delete = True
            if not is_delete:
                rec.contact_view_opportunity_count += mod_qty
            else:
                rec.contact_view_opportunity_count -= mod_qty
            parent_id = rec.parent_id.sudo()
            while parent_id:
                if not is_delete:
                    parent_id.contact_view_opportunity_count += mod_qty
                else:
                    parent_id.contact_view_opportunity_count -= mod_qty
                parent_id = parent_id.parent_id

    @api.depends('parent_id', 'child_ids', 'child_ids.sale_order_ids','child_ids.sale_order_ids.state', 'sale_order_ids','sale_order_ids.state', 'parent_id.sale_order_ids','parent_id.sale_order_ids.state')
    def _compute_contact_view_sale_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        for partner in all_partners:
            partner.contact_view_sale_count = partner.sale_order_count
            parent_id = partner.parent_id
            while parent_id:
                parent_id.contact_view_sale_count = parent_id.sale_order_count
                parent_id = parent_id.parent_id

    @api.depends('parent_id', 'child_ids', 'child_ids.purchase_line_ids.order_id','child_ids.purchase_line_ids.order_id.state','purchase_line_ids.order_id','purchase_line_ids.order_id.state',
                 'parent_id.purchase_line_ids.order_id','parent_id.purchase_line_ids.order_id.state')
    def _compute_contact_view_purchase_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        for partner in all_partners:
            partner.contact_view_purchase_count = partner.purchase_order_count
            parent_id = partner.parent_id
            while parent_id:
                parent_id.contact_view_purchase_count = parent_id.purchase_order_count
                parent_id = parent_id.parent_id

    @api.depends('parent_id', 'child_ids', 'child_ids.invoice_ids', 'invoice_ids.payment_state',
                 'parent_id.invoice_ids.payment_state', 'invoice_ids.state', 'parent_id.invoice_ids.state')
    def _compute_contact_view_invoice_amount(self):
        # if not self.ids:
        #     return True
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        for partner in all_partners:
            partner.contact_view_total_invoice = partner.total_invoiced
            parent_id = partner.parent_id
            while parent_id:
                parent_id.contact_view_total_invoice = parent_id.total_invoiced
                parent_id = parent_id.parent_id

    @api.depends('parent_id', 'child_ids', 'child_ids.invoice_ids', 'invoice_ids.payment_state',
                 'parent_id.invoice_ids.payment_state', 'invoice_ids.state', 'parent_id.invoice_ids.state')
    def _compute_contact_view_supplier_invoice_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        for partner in all_partners:
            partner.contact_view_supplier_invoice_count = partner.supplier_invoice_count
            parent_id = partner.parent_id
            while parent_id:
                parent_id.contact_view_supplier_invoice_count = parent_id.supplier_invoice_count
                parent_id = parent_id.parent_id

    @api.depends('parent_id.property_product_pricelist','parent_id', 'child_ids', 'country_id','property_product_pricelist')
    @api.depends_context('company')
    def _compute_contact_view_product_pricelist(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        for partner in all_partners:
            partner.contact_view_property_product_pricelist = partner.property_product_pricelist
            parent_id = partner.parent_id
            while parent_id:
                parent_id.contact_view_property_product_pricelist = parent_id.property_product_pricelist
                partner.contact_view_property_product_pricelist = parent_id.property_product_pricelist
                parent_id = parent_id.parent_id
