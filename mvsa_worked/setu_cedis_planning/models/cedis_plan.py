from odoo import fields, models


class CedisPlan(models.Model):
    _name = 'cedis.plan'
    _description = 'Cedis Planning'

    name = fields.Char(string='Name')
    picking_id = fields.Many2one(comodel_name='stock.picking', string='Transfer')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')
    user_ids = fields.Many2many('res.users', 'res_users_cedis_plan_rel', string='Multiple Responsible')
    picking_type_id = fields.Many2one(comodel_name='stock.picking.type', string='Operation Type')
    activity_type_id = fields.Many2one(comodel_name='mail.activity.type', string='Activity Type')
    urgent_order = fields.Boolean(string='Urgent Order')
    cliente_mostrador = fields.Boolean(string='Cliente Mostrador')
    detener_factura = fields.Boolean(string='Detener factura')
    summary = fields.Char(string='Summary')
    planning = fields.Char(string='Planning')
    sale_team_id = fields.Many2one('crm.team', string='Sales Team')
