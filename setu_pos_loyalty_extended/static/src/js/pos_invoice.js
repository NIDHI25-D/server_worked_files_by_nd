/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    //@Override
    //on latest odoo update added a new method for not download invoice
    shouldDownloadInvoice() {
        return false;
    },
});