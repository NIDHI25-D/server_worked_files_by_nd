import logging

from odoo import api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
_logger = logging.getLogger(__name__)

try:
    from statistics import mean
    STATS_PATH = tools.find_in_path('statistics')
except (ImportError, IOError) as err:
    _logger.debug(err)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def _compute_loc_accuracy(self):
        for rec in self:
            history = self.env['stock.inventory'].search([('location_ids', '=', rec.id), ('state', '=', 'done')])
            history = history.sorted(key=lambda r: r.write_date, reverse=True)
            rec.loc_accuracy = 0.0
            if history:
                wh = rec.get_warehouse()
                if wh.counts_for_accuracy_qty and len(history) > wh.counts_for_accuracy_qty:
                    rec.loc_accuracy = mean(history[:wh.counts_for_accuracy_qty].mapped('inventory_accuracy'))
                else:
                    rec.loc_accuracy = mean(history.mapped('inventory_accuracy'))

    discrepancy_threshold = fields.Float(
        string='Maximum Discrepancy Rate Threshold',
        digits=(3, 2),
        help="Maximum Discrepancy Rate allowed for any product when doing "
             "an Inventory Adjustment. Thresholds defined in Locations have "
             "preference over Warehouse's ones.")

    zero_confirmation_disabled = fields.Boolean(
        string='Disable Zero Confirmations',
        help='Define whether this location will trigger a zero-confirmation '
             'validation when a rule for its warehouse is defined to perform '
             'zero-confirmations.',
    )
    cycle_count_disabled = fields.Boolean(
        string='Exclude from Cycle Count',
        help='Define whether the location is going to be cycle counted.',
    )
    qty_variance_inventory_threshold = fields.Float(
        string='Acceptable Inventory Quantity Variance Threshold',
    )
    loc_accuracy = fields.Float(
        string='Inventory Accuracy', compute='_compute_loc_accuracy',
        digits=(3, 2),
    )


    def _get_zero_confirmation_domain(self):
        self.ensure_one()
        domain = [
            ('location_id', '=', self.id),
            ('quantity', '>', 0.0),
        ]
        return domain


    def check_zero_confirmation(self):
        pass


    def create_zero_confirmation_cycle_count(self):
        pass


    def action_accuracy_stats(self):
        self.ensure_one()
        action = self.env.ref('stock_cycle_count.act_accuracy_stats')
        result = action.read()[0]
        result['context'] = {"search_default_location_id": self.id}
        new_domain = result['domain'][:-1] + \
            ", ('location_ids', 'child_of', active_ids)]"
        result['domain'] = new_domain
        return result
