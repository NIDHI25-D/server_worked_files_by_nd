import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(OrderWidget.prototype, {

    //@Override -- For Adding Non Service Products count in Order Screen
    get_total_articls_count() {
        debugger
        var total_articles = 0;
        this.props.lines.forEach((line)=> {
//                if($.inArray(line.product.detailed_type, ['consu','product']) >-1 && line.product.sale_ok)
            if (line.product_id && line.product_id.type != 'service'){
                total_articles += line.qty;
            }
        });
        return total_articles;
    }
});
