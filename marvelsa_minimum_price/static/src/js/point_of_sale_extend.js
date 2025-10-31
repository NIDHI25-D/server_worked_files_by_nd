debugger
/** @odoo-module **/
const {registry} = require("@web/core/registry");
const {PaymentScreen} = require("@point_of_sale/app/screens/payment_screen/payment_screen");
const {_t} = require("@web/core/l10n/translation");
import { patch } from "@web/core/utils/patch";
import { WarningDialog } from "@web/core/errors/error_dialogs";

patch(PaymentScreen.prototype, {

    async validateOrder(isForceValidate) {
        debugger;
        if (this.check_min_price(isForceValidate)) {
            return super.validateOrder(...arguments);
        }
    },
    check_min_price(force_validation) {
        debugger
        var self = this;
        var order = this.pos.get_order();
        var orderlines = order.get_orderlines();

        if(this.pos.config.enable_disable_minimum_price){
            var list = []
            if (orderlines.length > 0){
                for(var i = 0; i < orderlines.length; i++){
                    var orderline = orderlines[i];
                    var base_price = orderline.get_base_price();
                    var minimum_price = orderline.product_id["minimum_price"];
                    if(base_price < minimum_price){
                        list.push(orderline.product_id["display_name"])
                    }
                }
            }
            if(list && list.length){
                this.dialog.add(WarningDialog, {

                title: _t('Price is lower than the minimum product price!'),
                message: _t('Please recheck ') + list
                });
                    return false;
            }
        }
        return true
    }
});
