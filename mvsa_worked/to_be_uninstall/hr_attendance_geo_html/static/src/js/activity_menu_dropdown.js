/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { Dropdown } from "@web/core/dropdown/dropdown";

patch(Dropdown.prototype, {
    openPopover() {
        /*
            Author: varshil.galathia@setconsulting.com
            Date: 06/02/2025
            Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
            Purpose: Inherited the method to Check if the Location Access is not Granted only when User is doing 
            the "Check In/Out" Operations without Location Permission.
        */
        
        // Ensure the dropdown opened exclusively for the 'Check In' or 'Check Out' operation. #Varshil
        if (this.props.beforeOpen && this.props.beforeOpen.name && this.props.beforeOpen.name == "bound searchReadEmployee"){
            navigator.geolocation.getCurrentPosition(
                async ({coords: {latitude, longitude}}) => {
                   super.openPopover();
                },
                async err => {
                    await rpc("/hr_attendance_geo_html/raise_location_access_error");
                },
                {
                    enableHighAccuracy: true,
                }
            )
        } else {
            super.openPopover();
        }
    }

});