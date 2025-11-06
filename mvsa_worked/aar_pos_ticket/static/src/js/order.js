odoo.define('aar_pos_ticket_receipt.order', function (require) {
    "use strict";

    const {Order, Orderline} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const SetuPosTicket = (Order) => class SetuPosTicket extends Order {
        constructor() {
            super(...arguments);
        }

        init_from_JSON(json) {
            var res = super.init_from_JSON(...arguments);
            if (json.ean13) {
                this.ean13 = json.ean13;
            }
            return res;
        }

        export_as_JSON() {
            var json = super.export_as_JSON(...arguments);

            if (this.ean13) {
                json.ean13 = this.ean13;
            }
            if (!this.ean13 && this.uid) { // init ean13 and automatic create ean13 for order
                var ean13 = '998';
                if (this.pos.user.id) {
                    ean13 += this.pos.user.id;
                }
                if (this.sequence_number) {
                    ean13 += this.sequence_number;
                }
                if (this.pos.config.id) {
                    ean13 += this.pos.config.id;
                }
                var fean13 = this.uid.split('-');
                for (var i in fean13) {
                    ean13 += fean13[i];
                }
                ean13 = ean13.split("");
                var aean13 = []
                var sean13 = ""
                for (var i = 0; i < ean13.length; i++) {
                    if (i < 12) {
                        sean13 += ean13[i]
                        aean13.push(ean13[i])
                    }
                }
                this.ean13 = sean13 + this.generate_ean13(aean13).toString()
            }
            return json;
        }

        generate_ean13(code) {
            if (code.length != 12) {
                return -1
            }
            var evensum = 0;
            var oddsum = 0;
            for (var i = 0; i < code.length; i++) {
                if ((i % 2) == 0) {
                    evensum += parseInt(code[i])
                } else {
                    oddsum += parseInt(code[i])
                }
            }
            var total = oddsum * 3 + evensum
            return parseInt((10 - total % 10) % 10)
        }

//        fix_tax_included_price(line) {
//            debugger
//            super.fix_tax_included_price(...arguments);
//            if (this.fiscal_position) {
//                var unit_price = line.product['list_price'];
//                var taxes = line.get_taxes();
//                var mapped_included_taxes = [];
//                _(taxes).each(function (tax) {
//                    var line_tax = line._map_tax_fiscal_position(tax);
//                    if (tax.price_include && tax.id != line_tax.id) {
//
//                        mapped_included_taxes.push(tax);
//                    }
//                })
//                if (mapped_included_taxes.length > 0) {
//                    unit_price = line.compute_all(mapped_included_taxes, unit_price, 1, this.pos.currency.rounding, true).total_excluded;
//                    line.set_unit_price(unit_price);
//                }
//            }
//        }

    }
    Registries.Model.extend(Order, SetuPosTicket);

    const SetuPosTicketLine = (Orderline) => class SetuPosTicketLine extends Orderline {
        export_for_printing() {
            var line = super.export_for_printing(...arguments);
            line.default_code = this.get_product().default_code;
            return line;
        }
    }
    Registries.Model.extend(Orderline, SetuPosTicketLine);
});
