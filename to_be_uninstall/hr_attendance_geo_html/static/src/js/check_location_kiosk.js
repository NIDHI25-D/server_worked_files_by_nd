import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

async function checkLocationKiosk(env, action) {
    /*
        Author: varshil.galathia@setconsulting.com
        Date: 06/02/2025
        Task: Hr Attendance Professional Policy Geolocation via html5 Geolocate
        Purpose: New the method to Check if the Location Access is not Granted only when User is doing 
        the "Check In/Out" Operations without Location Permission.
    */
    const { CompanyId } = action.params;
    
    navigator.geolocation.getCurrentPosition(
        async ({coords: {latitude, longitude}}) => {
            browser.open(`/hr_attendance/kiosk_mode_menu/${CompanyId}`, "_self");
        },
        async err => {
            await rpc("/hr_attendance_geo_html/raise_location_access_error");
        },
        {
            enableHighAccuracy: true,
        }
    )
}

registry.category("actions").add("check_location_kiosk", checkLocationKiosk);
