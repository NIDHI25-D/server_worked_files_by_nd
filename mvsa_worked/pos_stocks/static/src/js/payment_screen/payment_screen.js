import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { onMounted } from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => {
            if (this.currentOrder && this.currentOrder.partner_id) {
                this.currentOrder.l10n_mx_edi_cfdi_to_public =
                    this.currentOrder.partner_id.l10n_mx_edi_cfdi_to_public || false;

                this.currentOrder.l10n_mx_edi_usage =
                    this.currentOrder.partner_id.l10n_mx_edi_usage || "G01";

                this.currentOrder.set_to_invoice(true);
            }
        });
    },
});
