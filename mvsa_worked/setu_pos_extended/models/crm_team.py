from odoo import fields, models, api


class CrmTeam(models.Model):
    _name = "crm.team"
    _inherit = ["crm.team", "pos.load.mixin"]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ["id", "name"]

    @api.model
    def _load_pos_data_domain(self, data):
        return []