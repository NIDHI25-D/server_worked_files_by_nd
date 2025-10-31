from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.depends('line_ids.product_qty', 'line_ids.theoretical_qty')
    def _compute_over_discrepancy_line_count(self):
        for inventory in self:
            lines = inventory.line_ids.filtered(lambda line: line.discrepancy_percent > line.discrepancy_threshold)
            inventory.over_discrepancy_line_count = len(lines)

    @api.depends("state", "line_ids")
    def _compute_inventory_accuracy(self):
        for inv in self:
            theoretical = sum(inv.line_ids.mapped(lambda x: abs(x.theoretical_qty)))
            abs_discrepancy = sum(inv.line_ids.mapped(lambda x: abs(x.discrepancy_qty)))
            if theoretical:
                inv.inventory_accuracy = max(100.0 * (theoretical - abs_discrepancy) / theoretical, 0.0)
            if not inv.line_ids and inv.state == 'done':
                inv.inventory_accuracy = 100.0

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('pending', 'Pending to Approve'),
        ('done', 'Validated')]

    state = fields.Selection(
        selection=INVENTORY_STATE_SELECTION,
        string='Status', readonly=True, index=True, copy=False,
        help="States of the Inventory Adjustment:\n"
             "- Draft: Inventory not started.\n"
             "- In Progress: Inventory in execution.\n"
             "- Pending to Approve: Inventory have some discrepancies "
             "greater than the predefined threshold and it's waiting for the "
             "Control Manager approval.\n"
             "- Validated: Inventory Approved.")

    over_discrepancy_line_count = fields.Integer(
        string='Number of Discrepancies Over Threshold',
        compute='_compute_over_discrepancy_line_count',
        store=True)

    cycle_count_id = fields.Many2one(
        comodel_name='stock.cycle.count', string='Stock Cycle Count',
        ondelete='restrict', readonly=True)
    inventory_accuracy = fields.Float(
        string='Accuracy', compute='_compute_inventory_accuracy',
        digits=(3, 2), store=True, group_operator="avg")

    exclude_sublocation = fields.Boolean(string='Exclude Sublocations', default=False, tracking=True, readonly=True, states={'draft': [('readonly', False)]})

    def _get_inventory_lines_values(self):
        """Discard inventory lines that are from sublocations if option
        is enabled.

        Done this way for maximizing inheritance compatibility.
        """
        vals = super()._get_inventory_lines_values()
        if not self.exclude_sublocation:
            return vals
        new_vals = []
        for val in vals:
            if val['location_id'] in self.location_ids.ids:
                new_vals.append(val)
        return new_vals

    def _update_cycle_state(self):
        for inv in self:
            if inv.cycle_count_id and inv.state == 'done':
                inv.cycle_count_id.state = 'done'
        return True

    def action_validate(self):
        res = super(StockInventory, self).action_validate()
        self._update_cycle_state()
        return res

    def action_force_done(self):
        res = super(StockInventory, self)._action_done()
        self._update_cycle_state()
        return res

    def _check_group_inventory_validation_always(self):
        grp_inv_val = self.env.ref('stock_cycle_count.group_stock_inventory_validation_always')
        if grp_inv_val in self.env.user.groups_id:
            return True
        else:
            raise UserError(
                _('The Qty Update is over the Discrepancy Threshold.\n '
                  'Please, contact a user with rights to perform '
                  'this action.')
            )

    def _action_done(self):
        for inventory in self:
            if inventory.over_discrepancy_line_count and inventory.line_ids.filtered(
                    lambda t: t.discrepancy_threshold > 0.0):
                if inventory.env.context.get('normal_view', False):
                    self.write({'state': 'pending'})
                    return True
                else:
                    inventory._check_group_inventory_validation_always()
        res = super(StockInventory, self)._action_done()
        self._update_cycle_state()
        return res

    def write(self, vals):
        for inventory in self:
            if (inventory.cycle_count_id and 'state' not in vals.keys() and inventory.state != 'draft'):
                raise UserError(_('You cannot modify the configuration of an Inventory '
                                  'Adjustment related to a Cycle Count.'))
        return super(StockInventory, self).write(vals)
