from odoo import fields, models, api
from odoo.osv import expression
import ast
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


class PriorityRules(models.Model):
    _name = 'priority.rules'
    _inherit = ['mail.thread']
    _order = 'priority'

    name = fields.Char(string='Name')
    priority = fields.Integer(string="Priority set", copy=False)
    transfer_domain = fields.Char(default="[]")
    active = fields.Boolean(default=True)

    def cron_prioritization_of_pickings(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 06/03/25
            Task: Migration to v18 from v16
            Purpose: prioritization of the pickings when executing a cron as per the priority of the pickings.
        """
        team_complexity_dict = {}
        pickings_dict = {}
        for rules in self.search([]):
            domain_str = rules.transfer_domain
            domain = ast.literal_eval(domain_str) # remove strings from the domain
            pickings_dict[rules.name] = []
            for team in self.env['assortment.team'].search([]).sorted(key=lambda ct: ct.suggested_complex_id.end_range_of_lines, reverse=True):
                complexity = team.suggested_complex_id
                warehouse = team.warehouse_id
                operation_types = team.warehouse_team_type_id.operation_types_ids
                team_type_id = team.warehouse_team_type_id.id  # Store team type id
                team_domain = domain + [
                    ('picking_type_id.warehouse_id', '=', warehouse.id),
                    ('picking_type_id', 'in', operation_types.ids)
                ]
                # Initialize team_type.id entry in team_complexity_dict if not already present
                if team_type_id not in team_complexity_dict:
                    team_complexity_dict[team_type_id] = {}
                # Initialize complexity entry in the sub-dictionary if not already present
                if complexity.id not in team_complexity_dict[team_type_id]:
                    team_complexity_dict[team_type_id][complexity.id] = 0
                # Fetch existing pickings for this team and complexity
                filter_of_complexity_with_picking = team.warehouse_team_type_id.complexity_assortment_team_type_ids.filtered(
                        lambda ct: ct.complexity_levels_id == team.suggested_complex_id and ct.stock_picking_ids)
                if filter_of_complexity_with_picking and not self.env['stock.picking'].search([('assortment_team_id','=',team.id),('complexity_assigned_id','=',filter_of_complexity_with_picking.complexity_levels_id.id), ('state', '=', 'assigned')]) and filter_of_complexity_with_picking.stock_picking_ids:
                    # Assigning only 1 picking present in the complexity with the respected team and removing from the combo table. Here no rules are considered.
                    assigning_picking_from_team_type = filter_of_complexity_with_picking.stock_picking_ids[0]
                    assigning_picking_from_team_type.update({
                        'assortment_team_id': team,
                        'prioritization_priority': 'no_rule',
                        'lines_quantity': len(assigning_picking_from_team_type.move_line_ids),
                        'complexity_assigned_id': filter_of_complexity_with_picking.complexity_levels_id.id,
                        'assignment_date_time': fields.Datetime.now(),
                        # 'responsible_person': team.responsible_id.id,
                    })
                    _logger.info("Assigning Picking from team type : %s for Team : %s with Complexity : %s  ", assigning_picking_from_team_type.name, team.name,
                                 filter_of_complexity_with_picking.complexity_levels_id.name)
                    filter_of_complexity_with_picking.stock_picking_ids = [
                        (3, assigning_picking_from_team_type.id)]
                    team_complexity_dict[team_type_id][complexity.id] += len(
                        filter_of_complexity_with_picking.stock_picking_ids.mapped('move_line_ids'))
                excluded_ids = filter_of_complexity_with_picking.stock_picking_ids.ids if filter_of_complexity_with_picking else []
                # Fetch new pickings that are not yet assigned to a team
                picking = self.env['stock.picking'].search(
                    team_domain + [('assortment_team_id', '=', False), ('state', '=', 'assigned'),
                                   ('id', 'not in', excluded_ids) #,('responsible_person','=',False)
                                   ]
                ).filtered(
                    lambda pick: len(pick.move_line_ids) in range(
                        team.suggested_complex_id.initial_range_of_lines,
                        team.suggested_complex_id.end_range_of_lines
                    ) and not pick.assortment_team_id and len(pick.move_line_ids) <= team.warehouse_team_type_id.maximum_lines and pick.picking_type_id in operation_types
                )

                if picking:
                    for pick in picking:
                        complexity_type = self.env['complexity.levels'].search(
                            [('initial_range_of_lines', '<=', len(pick.move_line_ids)),
                             ('end_range_of_lines', '>=', len(pick.move_line_ids))])
                        # Ensure the total lines for this complexity do not exceed maximum_lines
                        if complexity_type and team_complexity_dict[team_type_id][complexity.id] + len(
                                pick.move_line_ids) <= team.warehouse_team_type_id.maximum_lines:
                            combo_type = team.warehouse_team_type_id.complexity_assortment_team_type_ids.filtered(
                                lambda ct: ct.complexity_levels_id == complexity_type)
                            if combo_type:
                                combo_type.stock_picking_ids = [(4, pick.id)]
                            else:
                                team.warehouse_team_type_id.complexity_assortment_team_type_ids = [
                                    (0, 0, {
                                        'complexity_levels_id': team.suggested_complex_id.id,
                                        'stock_picking_ids': [(4, pick.id)]})
                                ]
                            team_complexity_dict[team_type_id][complexity.id] += len(pick.move_line_ids)
                            if not isinstance(pickings_dict[rules.name], list):
                                pickings_dict[rules.name] = []
                            pickings_dict[rules.name].append(pick.name)

                    # Handle cases when there are no more pickings assigned to the team
                    if not self.env['stock.picking'].search([('complexity_assigned_id', 'in',
                                                              team.warehouse_team_type_id.complexity_assortment_team_type_ids.complexity_levels_id.ids),
                                                             ('assortment_team_id', '=', team.id),
                                                             ('state', '=', 'assigned'),
                                                             (
                                                             'complexity_assigned_id', '=', team.suggested_complex_id.id)]):
                        single_picking = team.warehouse_team_type_id.complexity_assortment_team_type_ids.filtered(
                            lambda ct: ct.complexity_levels_id == complexity).stock_picking_ids.sorted(
                            lambda p: len(p.move_line_ids))[0]
                        _logger.info("SINGLE PICKING : %s for Team : %s with Complexity : %s  ", single_picking.name, team.name,
                                     complexity.name)
                        single_picking.update({'assortment_team_id': team,
                                        'prioritization_priority':str(rules.priority),
                                        'lines_quantity':len(single_picking.move_line_ids),
                                        'complexity_assigned_id':team.suggested_complex_id,
                                        # 'responsible_person': team.responsible_id.id,
                                        'assignment_date_time': datetime.now(),
                                        })
                        single_picking.assortment_team_id.warehouse_team_type_id.complexity_assortment_team_type_ids.stock_picking_ids = [
                            (3, single_picking.id)]

        # Reassigning the pickings if high complexity is free.
        for team in self.env['assortment.team'].search([]):
            transfer_id = self.env['stock.picking'].search([('state','=','assigned'),('assortment_team_id','=',team.id),('complexity_assigned_id','=',team.suggested_complex_id.id)])
            if not transfer_id:
                complexicty_ids = team.warehouse_team_type_id.complexity_assortment_team_type_ids
                same_complexity_transfer_ids = complexicty_ids.filtered(lambda x:x.complexity_levels_id == team.suggested_complex_id)
                having_low_transfer_ids = True
                if not same_complexity_transfer_ids.stock_picking_ids:
                    while having_low_transfer_ids:
                        low_com_transfer = complexicty_ids.filtered(lambda x:x.complexity_levels_id.complexity_sequence > team.suggested_complex_id.complexity_sequence)
                        if not low_com_transfer:
                            having_low_transfer_ids = False
                        else:
                            lowest_complexity_transfer = low_com_transfer.sorted(
                                key=lambda x: x.complexity_levels_id.complexity_sequence
                            ).filtered(lambda x: x.stock_picking_ids)
                            if lowest_complexity_transfer.stock_picking_ids[0]:
                                picking = lowest_complexity_transfer.stock_picking_ids[0]
                                new_pick_complexity = team.warehouse_team_type_id.complexity_assortment_team_type_ids.search(
                                    [('stock_picking_ids', '=', picking.id)])
                                team_complexity_assigned = self.env['stock.picking'].search([('state','=','assigned'),('assortment_team_id','=',team.id),('complexity_assigned_id','=',new_pick_complexity.complexity_levels_id.id)])
                                if not team_complexity_assigned:
                                    old_combo_line = complexicty_ids.filtered(
                                        lambda x: picking in x.stock_picking_ids
                                    )
                                    if old_combo_line:
                                        old_combo_line.stock_picking_ids = [
                                            (3, picking.id)]
                                    picking.update({'assortment_team_id' : team,
                                                    'prioritization_priority':'no_rule',
                                                    'lines_quantity': len(picking.move_line_ids),
                                                    'complexity_assigned_id': new_pick_complexity.complexity_levels_id.id,
                                                    'assignment_date_time':fields.Datetime.now(),
                                                    # 'responsible_person': team.responsible_id.id,
                                                    })
                                    _logger.info("Reassigning lower complexity transfer %s to team %s with complexity %s",
                                                 picking.name, team.name,picking.complexity_assigned_id.name)
                            having_low_transfer_ids = False

        for team_id, complexity_lengths in team_complexity_dict.items():
            _logger.info("Team Type %s Complexities : %s ", team_id, complexity_lengths)
        _logger.info("Pickings Dict %s ", pickings_dict)
        _logger.info("TEAM COMPLEXITY  %s ", team_complexity_dict)

        return team_complexity_dict