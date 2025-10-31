odoo.define('stock_cycle_count.InventoryValidationController', function (require) {
"use strict";


var stockcyclecount = require('stock.InventoryValidationController')
var core = require('web.core');
var qweb = core.qweb;
var session = require('web.session');


stockcyclecount.include({
    renderButtons: function () {
        this._super.apply(this, arguments);
        session.user_has_group('stock_inv_ext.group_stock_inventory_supervisor').then(hasGroup => {
            if(hasGroup == false)
            {
                this.$buttons.find('.o_button_validate_inventory').remove()
            }

            console.log(hasGroup)
        });
    },
});
});