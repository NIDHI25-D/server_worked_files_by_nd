from odoo.addons.web.controllers.home import ensure_db, Home
from odoo import http
from odoo.http import request


class PackageHome(http.Controller):

    @http.route('/setu_package/<int:page>',type='http', auth='user')
    def redirect_to_package_form(self,**kwargs):
        """
            Author: jatin.babariya@setconsulting
            Date: 17/03/25
            Task: Migration from V16 to V18.
            Purpose: Show display of Scanned successfully and Show Packages left to be scanned By Scanning Scaner of Parcel tracking label.
        """
        package_id = kwargs.get('page')
        vals = {}
        if package_id:
            package_id = request.env['stock.quant.package'].sudo().browse(package_id)
            if not package_id.has_scanned:
                vals.update({'package':package_id})
                package_id.has_scanned = True
            picking_id = package_id.picking_id
            if picking_id and not picking_id.is_security_scanned_process:
                packages_without_scanned = picking_id.move_line_ids.result_package_id.filtered(lambda x: not x.has_scanned)
                vals.update({'packages_without_scanned': packages_without_scanned})
                if not packages_without_scanned:
                    picking_id.is_security_scanned_process = True
        if not vals:
            vals.update({'package':package_id})
        return request.render("setu_picking_control_by_pallets.scanned_package_template",vals)