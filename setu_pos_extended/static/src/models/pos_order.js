import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    //@Override -- Load Default Customer in pos as Configurable.
    set_screen_data(value) {
    const result = super.set_screen_data(value)
        if (! this.partner_id){
            var partner = this.config.default_partner_id
            debugger
            if (partner){
                this.set_partner(partner);
            }
        }
        return result
    }
});
