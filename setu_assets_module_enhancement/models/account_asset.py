from odoo import fields, models, api


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    is_it_computer_equipment = fields.Boolean('Is it computer equipment?')
    ram_memory_type_id = fields.Many2one('ram.memory.type')
    ram_memory_capacity_id = fields.Many2one('ram.memory.capacity')
    operative_system_type_id = fields.Many2one('operative.system.type')
    operative_system_distribution_id = fields.Many2one('operative.system.distribution',
                                                       domain="[('operative_system_type_id', '=', operative_system_type_id)]")
    operative_system_version_id = fields.Many2one('operative.system.version',
                                                  domain="[('operative_system_distribution_id', '=', operative_system_distribution_id)]")
    hard_disk_line_ids = fields.One2many('hard.disk.line', 'asset_id')
    network_card_line_ids = fields.One2many('network.card.line', 'asset_id')
    processor_model_id = fields.Many2one('processor.model')
    processor_speed_id = fields.Many2one('processor.speed')
    processor_generation_id = fields.Many2one('processor.generation')
    score = fields.Selection(string='Score', selection=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 20/01/25
            Task: Migration to v18 from v16
            Purpose: When selecting the model in asset whether to display the other_info page or not.
        """
        res = super(AccountAsset, self)._onchange_model_id()
        model = self.model_id
        if model:
            self.is_it_computer_equipment = model.is_it_computer_equipment
        return res

    @api.onchange('is_it_computer_equipment')
    def _onchange_is_it_computer_equipment(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 20/01/25
            Task: Migration to v18 from v16
            Purpose: When change the asset_models is_it_computer_equipment change in previous assets.
        """
        res = self.env['account.asset'].search(
            [('state', '!=', 'model'), ('parent_id', '=', False),
             ('model_id', '=', self._origin.id)])
        for asset in res:
            model = self
            if model:
                asset.is_it_computer_equipment = self.is_it_computer_equipment
