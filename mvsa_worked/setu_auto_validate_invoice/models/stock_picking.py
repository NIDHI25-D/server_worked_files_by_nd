from datetime import datetime
from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _action_done(self):
        """
            Author: siddharth@setuconsulting
            Date: 11/04/25
            Task: mvsa migration
            Purpose: To consider sale order of this transfer in auto sign
        """
        res = super(StockPicking, self)._action_done()
        for transfer in self:
            sale_id = transfer.sale_id
            if sale_id and transfer.picking_type_code == 'outgoing':
                sale_id.is_invoice_create_from_cron = True
        #         remove due to concurrent update { https://app.clickup.com/t/86dtfvu24 }
        return res
