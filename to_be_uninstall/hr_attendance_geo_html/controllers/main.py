from odoo import http, _
from odoo.http import request
from odoo.addons.to_be_uninstall.hr_attendance_base.controllers.main import HrAttendanceBase

class HrAttendanceGeoHtml(HrAttendanceBase):

    @http.route("/hr_attendance_geo_html/raise_location_access_error", type="json", auth="user")
    def raise_location_access_error(self):
        """
            Author: varshil.galathia@setconsulting.com
            Date: 06/02/2025
            Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
            Purpose: New method to Raise an UserError is that the Location Access is not Granted while doing the Check In/Out Operation.
            :return: The Error Message of Location Access Denied.
        """
        request.env["bus.bus"]._sendone(request.env.user.partner_id, "simple_notification", {
            "type": "danger",
            "title": _("Access Denied"),
            "message": _("Location Access has not been Granted, please Enable it to Proceed!"),
        })
