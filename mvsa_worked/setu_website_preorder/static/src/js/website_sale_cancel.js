/** @odoo-module **/
import publicWidget from '@web/legacy/js/public/public_widget';
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { SaleOrderPortalReorderWidget } from "@website_sale/js/website_sale_reorder";
import { rpc } from "@web/core/network/rpc";
const { Component, onRendered, xml } = owl;
import { formatCurrency } from "@web/core/currency";

publicWidget.registry.CancelOrderPortalWidget = publicWidget.Widget.extend({
    selector: ".o_portal_sidebar",
    events: {
        "click .o_wsale_cancel_button": "_onCancelOrder",
    },
    _onCancelOrder(ev){
//        debugger
        const orderId = parseInt(ev.currentTarget.dataset.saleOrderId);
        const urlSearchParams = new URLSearchParams(window.location.search);
        const currentDate = new Date(ev.currentTarget.dataset.saleOrderCurrentTime);
        const orderCancelLimitTime = new Date(ev.currentTarget.dataset.saleOrderCancelLimitTime);

        this.call("dialog", "add", CancelorderDialog, {
            orderId: orderId,
            accessToken: urlSearchParams.get("access_token"),
            currentDate: currentDate,
            orderCancelLimitTime:orderCancelLimitTime,
        });

    },
});


export class CancelorderDialog extends Component {
//debugger
    static template = "setu_website_preorder.cancelorderModal";

    static props = {
        close: Function,
        orderId: Number,
        accessToken: String,
        currentDate: Object,
        orderCancelLimitTime: Object,
    };

    static components = {
        Dialog,
    };

    setup() {
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this.formatCurrency = formatCurrency;
    }
    async confirmCancelorder(ev) {
//        debugger
        await rpc("/shop/cancel_order", {
        order_id: this.props.orderId,
        });
        window.location ="/my/orders/"+this.props.orderId+"?access_token="+this.props.accessToken
    }
}


