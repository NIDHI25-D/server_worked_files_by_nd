from odoo import api, fields, models, _
from odoo.addons.stock.models.stock_picking import Picking
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


def action_put_in_pack(self):
    """
        Author: jatin.babariya@setconsulting
        Date: 17/03/25
        Task: Migration from V16 to V18.
        Purpose: To create massive packages open form view of choose delivery package, Set Move lines, This method call on button massive package in Transfer.
    """
    self.ensure_one()
    if self.state not in ('done', 'cancel'):
        picking_move_lines = self.move_line_ids
        if (
                # not self.picking_type_id.show_reserved
                # and not self.immediate_transfer
                not self.env.context.get('barcode_view')
        ):
            picking_move_lines = self.move_line_ids

        move_line_ids = picking_move_lines.filtered(lambda ml:
                                                    float_compare(ml.quantity, 0.0,
                                                                  precision_rounding=ml.product_uom_id.rounding) > 0 and not ml.result_package_id and ml.product_id.package_type)

        if not move_line_ids and picking_move_lines._context.get('massive_package'):
            if picking_move_lines.filtered(
                    lambda prod: not prod.product_id.package_type and prod.qty_done and not prod.result_package_id):
                # If there are no move_lines but user clicks massive_package button then  this error is raised. When there would be a sigle product and scenario appears from that case this error is raised.
                raise UserError(
                    _("To continue the Massive Package process, kindly enable the Package Type in the Product %s. Either Put in Pack the product or remove the done quantity",
                      picking_move_lines.filtered(lambda prod: not prod.product_id.package_type).mapped(
                          'product_id.name')))
            raise UserError(
                _("You need to establish a quantity to continue or packages are not possible as package is already."))
        if not move_line_ids and picking_move_lines._context.get(
                'massive_package') and self.picking_type_id.code == 'outgoing':
            move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.qty_done, 0.0,
                                                                                 precision_rounding=ml.product_uom_id.rounding) > 0 and ml.result_package_id and ml.product_id.package_type)
            if move_line_ids and move_line_ids.filtered(lambda ml: ml._context.get('massive_package')):
                raise UserError(_("You can't create massive packages as packages are already created"))
            elif move_line_ids and picking_move_lines.filtered(lambda ml: ml.product_id.package_type):
                raise UserError(_("You can't put in pack for already done packages."))
        if not self._context.get('massive_package'):
            move_line_ids = picking_move_lines.filtered(
                lambda ml: float_compare(ml.qty_done, 0.0,
                                         precision_rounding=ml.product_uom_id.rounding) > 0 and not ml.result_package_id)
        if not move_line_ids:
            move_line_ids = picking_move_lines.filtered(lambda ml: float_compare(ml.quantity, 0.0,
                                                                                 precision_rounding=ml.product_uom_id.rounding) > 0 and float_compare(
                ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding) == 0 and not ml.result_package_id)
        if move_line_ids:
            _logger.info('Move Lines : %s', move_line_ids)
            res = self._pre_put_in_pack_hook(move_line_ids)
            if not res:
                res = self._set_delivery_package_type()
            return res
        else:
            raise UserError(
                _("Please add 'Done' quantities to the picking to create a new pack or packages are present"))


Picking.action_put_in_pack = action_put_in_pack


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    package_count = fields.Integer(string="Package count", compute='_compute_pickings_packges', store=True)
    pallet_count = fields.Integer(string="Pallet count", compute='_compute_pickings_packges', store=True)
    box_count = fields.Integer(string="Box count", compute='_compute_pickings_packges', store=True)
    is_security_scanned_process = fields.Boolean(default=False, string="Security scanned process")

    @api.depends('state')
    def _compute_pickings_packges(self):
        """
            Author: nidhi@setconsulting
            Date: 05/08/25
            Task: Pickings Issue { https://app.clickup.com/t/86dxeawme}
            Purpose: To compute picking packages. The package count, pallet count, and Box count fields are not displaying the correct information.
            They are displaying the product records inside the packages instead of package quantities. change code

            script: execute for old records
             import logging
             _logger = logging.getLogger(__name__)
            picking_ids = self.env['stock.picking'].search([('state','=','done')])
            picking_ids = self.env['stock.picking'].browse([817625,817624])
            _logger.info("Compute _compute_pickings_packges method box,pallet,package start")
            _logger.info(f"Compute _compute_pickings_packges method box,pallet,package, picking_ids: {picking_ids}")
            for pick in picking_ids:
                package = 0
                box = 0
                pallets = 0
                for package_id in pick.package_level_ids.package_id:
                    if package_id.package_type == 'bundle_package':
                       package += 1
                    if package_id.package_type == 'pallet':
                       pallets += 1
                    if package_id.package_type == 'box':
                       box += 1
                pick.package_count = package
                pick.pallet_count = pallets
                pick.box_count = box
            _logger.info("Compute _compute_pickings_packges method box,pallet,package modification end")
        """
        _logger.debug("Compute _compute_pickings_packges method start")
        for pick in self:
            package = 0
            box = 0
            pallets = 0
            for package_id in pick.package_level_ids.package_id:
                if package_id.package_type == 'bundle_package':
                    package += 1
                if package_id.package_type == 'pallet':
                    pallets += 1
                if package_id.package_type == 'box':
                    box += 1
            pick.package_count = package
            pick.pallet_count = pallets
            pick.box_count = box
        _logger.debug("Compute _compute_pickings_packges method end")

    def button_validate(self):
        """
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18.
            Purpose: To Set picking in packages.
        """
        res = super(StockPicking, self).button_validate()
        for rec in self:
            for move in rec.move_line_ids:
                move.result_package_id.picking_id = rec.id
        return res

    def _put_in_pack(self, move_line_ids, create_package_level=True):
        """
            (overwrite the method)
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18 (Massive package button).
            Purpose: Single package is created for the products (in which Package Type boolean is enabled in products) mentioned in the Done qty of
                     PICK stock.move.line. This procedure will work only for Button: Massive Package.
                     So in code, to get the functionality proper, the number mentioned in done qty that many stock.move.line are created.
        """
        if move_line_ids.filtered(lambda prod: prod.product_id.package_type == True) and self._context.get(
                'massive_package_method'):
            move_line_ids = move_line_ids.filtered(lambda prod: prod.product_id.package_type == True)
            multi_packages = self.env['stock.quant.package']
            for pick in self:
                for ml in move_line_ids:
                    moves_lines_to_pack = self.env['stock.move.line']
                    done_to_keep = ml.quantity
                    vals = {'quantity': ml.quantity}
                    new_move_line = ml.copy(
                        default={'quantity': 0})
                    ml.write(vals)
                    new_move_line.write({'quantity': done_to_keep})
                    moves_lines_to_pack |= new_move_line
                    for quantities in range(int(done_to_keep) - 1):
                        package = self.env['stock.quant.package'].create({})
                        move_lines_to_pack = self.env['stock.move.line']
                        new_move_line_done_qty = ml.copy(
                            default={'quantity': 0.0})
                        new_move_line.update({'quantity': new_move_line.quantity - 1})
                        ml.update({'quantity': ml.quantity - 1})
                        new_move_line_done_qty.write({'quantity': 1.0})
                        move_lines_to_pack |= new_move_line_done_qty
                        package_type = move_lines_to_pack.move_id.product_packaging_id.package_type_id
                        if len(package_type) == 1:
                            package.package_type_id = package_type
                        if len(move_lines_to_pack) == 1:
                            default_dest_location = move_lines_to_pack._get_default_dest_location()
                            move_lines_to_pack.location_dest_id = default_dest_location._get_putaway_strategy(
                                product=move_lines_to_pack.product_id,
                                quantity=move_lines_to_pack.quantity,
                                package=package)
                        move_lines_to_pack.write({
                            'result_package_id': package.id,
                        })
                        package_level = self.env['stock.package_level'].create({
                            'package_id': package.id,
                            'picking_id': pick.id,
                            'location_id': False,
                            'location_dest_id': move_lines_to_pack.mapped('location_dest_id').id,
                            'move_line_ids': [(6, 0, move_lines_to_pack.ids)],
                            'company_id': pick.company_id.id,
                        })
                        multi_packages |= package
                    packages = self.env['stock.quant.package'].create({})
                    package_type = moves_lines_to_pack.move_id.product_packaging_id.package_type_id
                    if len(package_type) == 1:
                        packages.package_type_id = package_type
                    if len(moves_lines_to_pack) == 1:
                        default_dest_location = moves_lines_to_pack._get_default_dest_location()
                        moves_lines_to_pack.location_dest_id = default_dest_location._get_putaway_strategy(
                            product=moves_lines_to_pack.product_id,
                            quantity=moves_lines_to_pack.quantity,
                            package=packages)
                    moves_lines_to_pack.write({
                        'result_package_id': packages.id,
                    })
                    _logger.info('Moves lines to pack : %s', moves_lines_to_pack)
                    if len(pick) == 1:
                        package_level = self.env['stock.package_level'].create({
                            'package_id': packages.id,
                            'picking_id': pick.id,
                            'location_id': False,
                            'location_dest_id': moves_lines_to_pack.mapped('location_dest_id').id,
                            'move_line_ids': [(6, 0, moves_lines_to_pack.ids)],
                            'company_id': pick.company_id.id,
                        })
                    multi_packages |= packages
                    # task: Error in the put in back button with partialities, url: https://app.clickup.com/t/86dx9vdz5
                    # remove this condition because if fraction qty given it did not delete old line.
                    # if ml.quantity == 1:
                    if ml.quantity:
                        ml.unlink()
                # pick.action_assign()
            package_type = self._context.get('method_massive_package')
            for quant_package in multi_packages:
                quant_package.write({'package_type': package_type,
                                     'picking_id': quant_package.picking_id.id if quant_package.picking_id else False,
                                     'sale_order_id': quant_package.picking_id.sale_id.id if quant_package.picking_id and quant_package.picking_id.sale_id else False,
                                     'customer_id': quant_package.picking_id.partner_id.id if quant_package.picking_id else False})
            return multi_packages
        else:
            res = super(StockPicking, self)._put_in_pack(move_line_ids)
            # self.action_assign()
            if res:
                for quant_package in res:
                    package_type = self._context.get('package_type')
                    if package_type:
                        quant_package.write({'package_type': package_type,
                                             'picking_id': quant_package.picking_id.id if quant_package.picking_id else False,
                                             'sale_order_id': quant_package.picking_id.sale_id.id if quant_package.picking_id and quant_package.picking_id.sale_id else False,
                                             'customer_id': quant_package.picking_id.partner_id.id if quant_package.picking_id else False})
            return res

    def action_massive_package(self):
        """
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18.
            Purpose: To call method action_put_in_pack by clicking on Massive Package Button.
        """
        return self.with_context(massive_package=True).action_put_in_pack()
