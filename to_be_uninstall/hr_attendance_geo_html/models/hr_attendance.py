from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    is_geo_access_check_in = fields.Html(string="Geolocation In", readonly=True, compute="_compute_is_geo_access_check_in", store=True)
    is_geo_access_check_out = fields.Html(string="Geolocation Out", readonly=True, compute="_compute_is_geo_access_check_out", store=True)

    @api.depends("in_latitude", "in_longitude")
    def _compute_is_geo_access_check_in(self):
        """
            Author: varshil.galathia@setconsulting.com
            Date: 06/02/2025
            Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
            Purpose: New Compute method to set value of the field "is_geo_access_check_in". 
        """
        for rec in self:
            rec.is_geo_access_check_in = False
            if not rec.in_latitude or not rec.in_longitude:
                continue
            rec.is_geo_access_check_in  = '''
                <h5>   
                    <div>
                        <div style="padding-left: 2%;">
                            <i class="fa fa-check-square-o token-fa-3x" style="color:green; align: center;"></i>
                        </div>
                    </div>
                </h5>
            '''

    @api.depends("out_latitude", "out_longitude")
    def _compute_is_geo_access_check_out(self):
        """
            Author: varshil.galathia@setconsulting.com
            Date: 06/02/2025
            Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
            Purpose: New Compute method to set value of the field "is_geo_access_check_out".
        """
        for rec in self:
            rec.is_geo_access_check_out = False
            if not rec.out_latitude or not rec.out_longitude:
                continue
            rec.is_geo_access_check_out = '''
                <h5>
                    <div>
                        <div style="padding-left: 2%;">
                            <i class="fa fa-check-square-o token-fa-3x" style="color:green"></i>
                        </div>
                    </div>
               </h5>
            '''

