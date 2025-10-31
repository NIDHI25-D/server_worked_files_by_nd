/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { OutOfStockMessagePopup } from "@pos_stocks/app/out_of_stock_message_popup";
import { useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { PosStore, posService } from "@point_of_sale/app/store/pos_store";

patch(posService, {
    dependencies: ["dialog", ...posService.dependencies],
});
patch(PosStore.prototype, {
    async setup({ dialog }) {

        this.dialog = dialog;
        await super.setup(...arguments);
    },


    set_stock_qtys(result) {
    var all = document.querySelectorAll(".product");
    if (result) {
        all.forEach((value) => {
            var product_id = value.getAttribute("data-product-id");
            var stock_qty = result[product_id];
            var qtyTag = value.querySelector(".qty-tag");
            if (qtyTag) {
                qtyTag.textContent = stock_qty;
            }
        });
    }
},


    wk_change_qty_css() {
      var self = this;
      const orders = this.models["pos.order"].filter((order) => !order.finalized);
      var wk_order = orders;
      var wk_p_qty = new Array();
      var wk_product_obj = self.wk_product_qtys;
      if (wk_order) {
        for (var i in wk_product_obj)
          wk_p_qty[i] = self.wk_product_qtys[i];
        for (var i = 0; i < wk_order.length; i++) {
          if (!wk_order[i].is_return_order) {
            var wk_order_line = wk_order[i].get_orderlines();
            for (var j = 0; j < wk_order_line.length; j++) {
              if (!wk_order_line[j].stock_location_id)
                wk_p_qty[wk_order_line[j].product_id.id] = wk_p_qty[wk_order_line[j].product_id.id] - wk_order_line[j].qty;
              let qtyTag = document.querySelector("#qty-tag" + wk_order_line[j].product_id.id);
              var qty = wk_p_qty[wk_order_line[j].product_id.id];
              if (qty && qtyTag) {
                    qtyTag.textContent = qty;
                }
              else {
                if (qtyTag) {
                    qtyTag.textContent = "0";
                    }
              }
            }

          }
        }
      }
    },


    async addLineToOrder(vals, order, opts = {}, configure = true) {
      var self = this;

      opts = opts || {};
      // warehouse management compatiblity code start---------------
      for (var i = 0; i < order.lines; i++) {
      if ((order.lines[i].product.id == product.id) && order.lines[i].stock_location_id) {
          opts.merge = false;
        }
      }

      // warehouse management compatiblity code end---------------
      if (
        !order.config.wk_continous_sale && order.config.wk_display_stock &&
        !self.get_order().is_return_order
      ){
        var qty_count = 0;
        let qtyElement = document.querySelector("#qty-tag" + vals.product_id.id);
        if (qtyElement ? parseInt(qtyElement.textContent) : 0)
          qty_count = (qtyElement ? parseInt(qtyElement.textContent) : 0);
        else {
          var wk_order = order;
          var wk_p_qty = new Array();
          var qty;
          var wk_product_obj = self.wk_product_qtys;
          if (wk_order) {
            for (var i in wk_product_obj)
              wk_p_qty[i] = self.wk_product_qtys[i];
            var orderline = wk_order.lines;
            for (var j = 0; j < orderline.length; j++) {
            if (!orderline[j].stock_location_id && vals.product_id.id == orderline[j].product_id.id)
            wk_p_qty[orderline[j].product_id.id] =
                      wk_p_qty[orderline[j].product_id.id] - orderline[j].qty;

            }
            qty = wk_p_qty[vals.product_id.id];
          }
          qty_count = qty || 0;
        }
        if (qty_count <= self.config.wk_deny_val && vals.product_id.type != 'service'){
             this.dialog.add(OutOfStockMessagePopup, {
                title: _t("Warning !!!!"),
                body: _t(
                  "(" + vals.product_id.display_name + ")" +
                  self.config.wk_error_msg + "."
                ),
            });
            return super.addLineToOrder(...arguments);
            }
        else return super.addLineToOrder(...arguments);
      } else return super.addLineToOrder(...arguments);
      if (self.config.wk_display_stock && !self.is_return_order)
        self.wk_change_qty_css();

    },

});