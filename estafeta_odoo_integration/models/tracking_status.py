from odoo import models, fields

class EstafetaTrackingStatus(models.Model):
    _name = "estafeta.tracking.status"
    _description = "Estafeta Tracking Status"

    estafeta_code = fields.Char(string="Estafeta Code", copy=False)
    estafeta_english_name = fields.Char(string="English Name")
    estafeta_local_date_time = fields.Char(string="Local Datetime", copy=False)
    estafeta_spanish_name = fields.Char(string="Spanish Name", copy=False)
    estafeta_warehouse_code = fields.Char(string="Warehouse Code", copy=False)
    estafeta_warehouse_name = fields.Char(string="Warehouse Name", copy=False)
    picking_id = fields.Many2one("stock.picking",string="Transfer")
