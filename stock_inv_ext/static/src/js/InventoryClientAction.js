/** @odoo-module **/

//import {bus} from 'web.core';
import MainComponent from '@stock_barcode/components/main';
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(MainComponent.prototype, {
    async o_save_record(ev) {
        var self = this;
        debugger
        var field_name = self.env.model.backorderModel === 'stock.picking' ? 'qty_done': 'inventory_quantity';
        var model_name = self.env.model.backorderModel === 'stock.picking' ? 'stock.move.line': 'stock.quant';
        var lines_with_doneQty = self.lines.filter(function (line) {
            return line[field_name] > 0
        })
        var def;
        if (lines_with_doneQty.length < 1) {
            self.notification.add(_t("There is nothing to save!"), {type: "warning"})
            return
        }
        lines_with_doneQty.forEach((line) => {
            var data = {}
            data[field_name] = line[field_name]
            def = self.orm.call(
                model_name,
                "write",
                [line.id, data],
            ).then(function (result) {
            debugger
                if (result) {
                    self.notification.add(_t("The Record has been Saved"), {type: "success"})
                    self.env.model.trigger('history-back')
                }
            })
        });
    }
});
