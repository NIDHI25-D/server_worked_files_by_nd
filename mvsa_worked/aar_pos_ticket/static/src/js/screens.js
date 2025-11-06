odoo.define('aar_pos_ticket.screens', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    var core = require('web.core');
    var utils = require('web.utils');
    var round_pr = utils.round_precision;
    var _t = core._t;
    var gui = require('point_of_sale.Gui');
    var qweb = core.qweb;

    const PosReceiptLogoChrome = (OrderReceipt) =>
        class extends OrderReceipt {
            get receipt() {
                console.log(this.receiptEnv.receipt)
                try {
                    JsBarcode("#barcode", this.env.pos.get('selectedOrder').ean13, {
                        format: "EAN13",
                        displayValue: true,
                        fontSize: 20
                    });
                } catch (error) {
                }
                return this.receiptEnv.receipt;
            }
        };
    Registries.Component.extend(OrderReceipt, PosReceiptLogoChrome);
    return OrderReceipt;

});

odoo.define('aar_pos_ticket.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var _super = models.Order;
    models.Order = models.Order.extend({
        export_for_printing: function () {
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            json.hb = {
                company_street: this.pos.company.street

            };
            return json;
        },


    })
    var _super_orderline = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var json = _super_orderline.prototype.export_for_printing.apply(this, arguments);
            json.default_code = this.get_product().default_code;
            json.prod_name = this.get_product().product_tmpl_id.name,
                console.log("orderline" + json)
            return json;
        },
    });
})



