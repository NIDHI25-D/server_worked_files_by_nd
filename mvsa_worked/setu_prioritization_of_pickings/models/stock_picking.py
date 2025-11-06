from odoo import fields, models, api,_
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    assortment_team_id = fields.Many2one('assortment.team', string="Assortment Team")
    prioritization_priority = fields.Selection(
        [('null', 'None'),
         ('0', '0'),
         ('1', '1'),
         ('2', '2'),
         ('3', '3'),
         ('4', '4'),
         ('5', '5'),
         ('no_rule', 'No rule')],
        string="Prioritization Priority",
        default='null')
    lines_quantity = fields.Integer(string="Lines Quantity")
    complexity_assigned_id = fields.Many2one('complexity.levels', string="Complexity Assigned")
    assignment_date_time = fields.Datetime(string="Assignment date and time")


    def _action_done(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 06/03/25
            Task: Migration to v18 from v16
            Purpose:The Available field is marked as true once the picking is validated and also set the value of the next picking if there are Pending Transfers in a queue.
        """
        res = super(StockPicking, self)._action_done()
        for transfer in self:
            _logger.info("Current Picking for Prioritization of picking %s ", transfer.name)
            if transfer.assortment_team_id:
                transfer.assortment_team_id.available = True
                # Get the current team type and complexity assortment
                team_type = transfer.assortment_team_id.warehouse_team_type_id
                # Assign the next picking in the list to the team
                complexity = transfer.assortment_team_id.warehouse_team_type_id.complexity_assortment_team_type_ids.filtered(lambda x:x.complexity_levels_id.complexity_sequence > transfer.assortment_team_id.suggested_complex_id.complexity_sequence)
                if not complexity:
                    complexity = team_type.complexity_assortment_team_type_ids.filtered(
                        lambda x: x.complexity_levels_id == transfer.complexity_assigned_id)
                not_assigned_team_picking_ids = complexity.stock_picking_ids.filtered(lambda x : not x.assortment_team_id )
                if not not_assigned_team_picking_ids:
                    current_complexity = team_type.complexity_assortment_team_type_ids.filtered(
                        lambda x: x.complexity_levels_id == transfer.complexity_assigned_id)
                    if current_complexity.stock_picking_ids:
                        next_picking = current_complexity.stock_picking_ids.filtered(
                            lambda x: not x.assortment_team_id).sorted(lambda p: len(p.move_line_ids))[0]
                        _logger.info("Next Picking %s ", next_picking.name)
                        team = self.env['assortment.team'].search([('warehouse_team_type_id', '=', team_type.id), (
                        'suggested_complex_id', '=', complexity.complexity_levels_id.id)])
                        next_picking.update({'assortment_team_id': team.id,
                                             'complexity_assigned_id' : complexity.complexity_levels_id.id,
                                             'lines_quantity':len(next_picking.move_line_ids),
                                             'assignment_date_time':datetime.now(),
                                             'prioritization_priority':self.prioritization_priority,
                                             # 'responsible_person':team.responsible_id.id
                        })
                        _logger.info(
                            "Next Picking : %s \n Assortment team : %s \n Complexity : %s \n Assignment Date : %s",
                            next_picking.name,team.name, complexity.complexity_levels_id.name, datetime.now())
                        team_type.complexity_assortment_team_type_ids.stock_picking_ids = [(3, next_picking.id)]
                    else:
                        # If no pickings left of the same complexity, a different complexity within the same team type
                        other_complexity = team_type.complexity_assortment_team_type_ids.filtered(
                            lambda x: x != complexity and x.stock_picking_ids
                        )
                        if other_complexity:
                            next_picking = other_complexity.stock_picking_ids.sorted(lambda p: len(p.move_line_ids))[0]
                            combo_records = team_type.complexity_assortment_team_type_ids.search(
                                [('stock_picking_ids', '=', next_picking.id)])
                            team_id = self.env['assortment.team'].search(
                                [('warehouse_team_type_id', '=', team_type.id),
                                 ('suggested_complex_id', '=', complexity.complexity_levels_id.id)])
                            _logger.info("Next Picking with different complexity: %s ", next_picking.name)
                            next_picking.update({'assortment_team_id':team_id.id,
                                                 'complexity_assigned_id':combo_records.complexity_levels_id.id,
                                                 'assignment_date_time':datetime.now(),
                                                 'prioritization_priority':self.prioritization_priority,
                                                 'lines_quantity': len(next_picking.move_line_ids)
                                                 })
                            # if not next_picking.responsible_person:
                            #     next_picking.responsible_person = team_id.responsible_id.id
                            _logger.info(
                                "Next Picking : %s \n Assortment team : %s \n Different Complexity : %s \n Assignment Date : %s",
                                next_picking.name, next_picking.assortment_team_id.name,
                                complexity.complexity_levels_id.name, datetime.now()
                            )

                            other_complexity.stock_picking_ids = [(3, next_picking.id)]
                else:
                    complexity = team_type.complexity_assortment_team_type_ids.filtered(
                        lambda x: x.complexity_levels_id == transfer.complexity_assigned_id)
                    next_picking = complexity.stock_picking_ids[0] if complexity.stock_picking_ids else not_assigned_team_picking_ids.sorted(lambda p: len(p.move_line_ids))[0]
                    _logger.info("Next Picking %s ", next_picking.name)
                    next_picking.update({
                      'assortment_team_id': transfer.assortment_team_id,
                      'complexity_assigned_id': team_type.complexity_assortment_team_type_ids.search([('stock_picking_ids','=',next_picking.id)]).complexity_levels_id.id,
                      'lines_quantity': len(next_picking.move_line_ids),
                      'assignment_date_time': datetime.now(),
                      'prioritization_priority': 'no_rule',
                      # 'responsible_person': transfer.assortment_team_id.responsible_id.id
                    })
                    _logger.info("Next Picking : %s \n Assortment team : %s \n Complexity : %s \n Assignment Date : %s", next_picking.name, transfer.assortment_team_id.name,next_picking.complexity_assigned_id.name ,datetime.now())
                    team_type.complexity_assortment_team_type_ids.stock_picking_ids = [(3, next_picking.id)]
                    if not not_assigned_team_picking_ids:
                        team_type.complexity_assortment_team_type_ids = [(2, complexity.id)]

        return res

'''
Cases : 
-->If C complexity picking is validated and there is picking in combo table then no need to assign other complexity
-->If validating c complexity and there are no other c complexity picking in combo table then assign lower complexity picking to the C complexity team with lower complexity.
'''