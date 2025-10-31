/** @odoo-module **/
debugger
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
debugger

patch(PaymentScreen.prototype, {
            async validateOrder(isForceValidate) {
            debugger
                var self = this;
                var partner = this.pos.get_order().partner_id;
                if (partner && partner.is_customer_locked) {
                    self.dialog.add(AlertDialog, {
                        'title': _t('Locked!'),
                        'body': _t('Unable to process the order as this customer has been locked.'),
                    });
                    return false;
                }
                return super.validateOrder(...arguments);

        }
});