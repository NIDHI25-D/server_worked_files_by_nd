import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { WarningDialog } from "@web/core/errors/error_dialogs";
import { _t } from "@web/core/l10n/translation";


patch(ProductScreen.prototype, {
    //@Override -- For Adding Update Product Price restrictions for service type Products.
    onNumpadClick(buttonValue) {
        if (buttonValue == 'price'){
            if (this.currentOrder.get_selected_orderline().product_id.type === 'service'){
                this.dialog.add(WarningDialog, {
                    title: _t("Warning !!!"),
                    message: _t("You can not change the price of this product."),
                });
                return false;
            }
        }
        return super.onNumpadClick(...arguments);
    },
});
