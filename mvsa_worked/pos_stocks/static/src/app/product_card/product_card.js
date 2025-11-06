/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { Component, onWillStart } from "@odoo/owl";


Object.assign(ProductCard.props, {
    stockQuantity: { type: Number, optional: true },
});

patch(ProductCard.prototype, {
    setup() {
        super.setup();
    },

    get stockQuantity() {
        return this.props.stockQuantity ?? 0;
    }
});
