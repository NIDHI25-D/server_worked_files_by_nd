/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

async function fetchProductStock(pos) {
    try {

        const result = await rpc("/web/dataset/call_kw/res.config.settings/wk_pos_fetch_pos_stock", {
            model: "res.config.settings",
            method: "wk_pos_fetch_pos_stock",
            args: [{
                wk_stock_type: pos.config.wk_stock_type,
                wk_hide_out_of_stock: pos.config.wk_hide_out_of_stock,
                config_id: pos.config.id,
            }],
            kwargs: {},
        })
        pos.wk_product_qtys = result;
        this.wk_product_qtys = result;
    } catch (error) {
    }
}



patch(ProductScreen.prototype, {
 setup() {
        super.setup();
        fetchProductStock(this.pos);

        this.pos.set_stock_qtys(this.pos.wk_product_qtys);
        this.pos.wk_change_qty_css();
    },
    get productsToDisplay() {
    var self = this;

    const products = super.productsToDisplay;

    if (!self.pos.wk_product_qtys) {
        return products;
    }

    let filteredProducts = products;
    if (self.pos.config.wk_display_stock) {
    if(self.pos.config.wk_hide_out_of_stock){
        return products.filter(product => self.pos.wk_product_qtys[product.id] || product.is_loyalty_reward_products || product.type === 'service');
        }
    else{
        return products;
        }
    }
    else{
        return products;
        }
    },

    get_information(wk_product_id) {
      this.pos.wk_change_qty_css();
      if (this.pos.wk_product_qtys) {
        return this.pos.wk_product_qtys[wk_product_id];
      }
    }

});
