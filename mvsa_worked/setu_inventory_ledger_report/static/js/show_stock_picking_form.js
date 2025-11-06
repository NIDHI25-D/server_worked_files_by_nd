/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

// Task Id : 363
// Author : Kinnari Tank
// Date : 18/JUNE/2024
// Task : Open Stock Picking Record on click Transfer field of Stock Move


export class StockPickingForm extends Component {
    static props = { ...standardFieldProps };

    setup() {
        this.action = useService("action");

    }

    async openActivity(activity) {
        type: "object",
            resId: this.props.record.resId,
            name: "action_open_reference",
            resModel: "stock.move",
        });
    }

}
//StockPickingForm.template = "setu_inventory_ledger_report.StockPickingForm";

export const StockPickingForm = {
    component: StockPickingForm,
};

registry.category("fields").add("show_stock_picking_form", StockPickingForm);
