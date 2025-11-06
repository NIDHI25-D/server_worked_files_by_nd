/** @odoo-module **/

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    setup() {
        super.setup(...arguments);
    },

    set_quantity(quantity, keep_price) {
    let pending_wk_line_stock_qty = this.wk_line_stock_qty || 0;
      var self = this;
      let qtyElement = document.querySelector("#qty-tag" + self.product_id.id);
      if (qtyElement ? parseInt(qtyElement.textContent) : 0)
            this.wk_line_stock_qty = (qtyElement ? parseInt(qtyElement.textContent) : 0);
      // -------code for POS Warehouse Management----------------
      if (self.stock_location_id && quantity && quantity != "remove") {
        if (
          self.pos.get_order() &&
          self.pos.get_order().selected_orderline &&
          self.pos.get_order().selected_orderline.cid == self.cid
        ) {
        return {
                    title: _t("Warning !!!!"),
                    body: _t("Selected orderline product have different stock location, you can't update the qty of this orderline"),
        };
          return;
        } else {
          return super.set_quantity(...arguments);
        }
      }
      // -------code for POS Warehouse Management----------------
      if (
        !self.config.wk_continous_sale &&
        self.config.wk_display_stock &&
        isNaN(quantity) != true &&
        quantity != "" &&
        self.wk_line_stock_qty != 0.0 &&
        parseFloat(pending_wk_line_stock_qty) - parseFloat(quantity) <
        self.config.wk_deny_val &&
        this.product_id.type != 'service'
      ) {

          return {
                    title: _t("Warning !!!!"),
                    body: _t("(" + this.product_id.display_name + ")" + self.config.wk_error_msg + "." ),
                };

      } else {
          var wk_avail_pro = 0;
          var wk_pro_order_line = self.order_id.get_selected_orderline();
          if (!self.config.wk_continous_sale && self.config.wk_display_stock && wk_pro_order_line) {
            let qtyElement = document.querySelector("#qty-tag" + self.product_id.id);
            var wk_current_qty = (qtyElement ? parseInt(qtyElement.textContent) : 0);
            if (quantity == "" || quantity == "remove")
              wk_avail_pro = wk_current_qty + wk_pro_order_line;
            else wk_avail_pro = wk_current_qty + wk_pro_order_line.qty - quantity;
              var result = super.set_quantity(...arguments);
              return result
          } else {
            var result = super.set_quantity(...arguments);
            return result
          }
      }
    },

});