/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/checkout";
import { rpc } from "@web/core/network/rpc";
const WebsiteSaleCheckout = publicWidget.registry.WebsiteSaleCheckout;
import { registry } from "@web/core/registry";

WebsiteSaleCheckout.include({
//  add a event for the particular object of carrier to select for order.
    events: Object.assign({
        'click [name="carrier_selection"]': '_updateDeliveryCarrier',
        }, WebsiteSaleCheckout.prototype.events),
//  saving the value of carrier that is selected for order.
    async _updateDeliveryCarrier(radio) {
        debugger
        if ($(radio.currentTarget.parentElement).find('input')[0].checked) {
            return await rpc('/shop/set_delivery_method', {
                'shipping_carrier_id': $(radio.currentTarget).find('select').val()
            });
        }
    },
});
