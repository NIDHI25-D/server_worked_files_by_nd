from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _action_open_kiosk_mode(self):
        """
            Author: varshil.galathia@setconsulting.com
            Date: 06/02/2025
            Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
            Purpose: Override the method to return a custom client action that restricts the user 
            from performing check-in/check-out operations if location access has not been granted.
            :return: Client Action.  
        """
        return {
            "type": "ir.actions.client",
            "tag": "check_location_kiosk",
            "params": {
                "CompanyId": self.env.company.id,
            },
        }
