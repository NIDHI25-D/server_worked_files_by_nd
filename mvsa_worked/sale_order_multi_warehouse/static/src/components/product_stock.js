/** @odoo-module **/
import {registry} from "@web/core/registry";
import {usePopover} from "@web/core/popover/popover_hook";
import {useService} from "@web/core/utils/hooks";
import {localization} from "@web/core/l10n/localization";
import { _t } from "@web/core/l10n/translation";

import { Component } from "@odoo/owl";
class ProductWarehousePopOver extends Component {
    static template = "ProductWarehousePopOver";
}
//ProductWarehousePopOver.template = "ProductWarehousePopOver"
export class ProductStockField extends Component {
        static template = "ProductStockField";
        setup() {
            this.popover = useService("popover");
            this.orm = useService("orm");
            this.action = useService("action");

        }
    async onInfoClick(ev) {

        const data = await this.orm.call(this.props.record.resModel, "get_warehouses_stock",[this.props.record.resId]);
        if (this.popoverCloseFn) {
            this.closePopover();
        }
        this.popoverCloseFn = this.popover.add(
            ev.target,
            ProductWarehousePopOver,
            {
                title: _t("Stock By Warehouse"),
                line: data,
                onClose: this.closePopover,
            },
            {
                position: localization.direction === "rtl" ? "bottom" : "left",
            },
        );
    }
    closePopover() {
        this.popoverCloseFn();
        this.popoverCloseFn = null;
    }
}

export const productstockfield = {
    component: ProductStockField,
};
ProductStockField.components = { Popover: ProductStockField };
//ProductStockField.template = "ProductStockField";

registry.category("view_widgets").add("warehouses_stock", productstockfield);