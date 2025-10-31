/** @odoo-module **/
debugger
    import publicWidget from "@web/legacy/js/public/public_widget";
    import "@website_sale/js/website_sale";
    import { session } from "@web/session";
    import { _t } from "@web/core/l10n/translation";
    import { rpc } from "@web/core/network/rpc";
debugger
    publicWidget.registry.WebsiteSale.include({
        async _onClickAdd(ev) {
            debugger
            var self = this;
            const _super = this._super.bind(this, ...arguments);
            var args = ev;

            ev.preventDefault();

            var $form = $(ev.currentTarget).closest('form');
            if ($("input[name='product_id']").is(':radio'))
                var product_id = $("input[name='product_id']:checked").attr('value');
            else
                var product_id = $("input[name='product_id']").attr('value');
            var add_qty = 1
            debugger
            await rpc("/shop/cart/update_json/check_elegible", {
                'product_id': product_id,
                'add_qty': add_qty
            })
            .then(function(result) {
                if (result.status == 'deny') {
                    debugger
                    location.reload()
                } else {
                    $('#add_to_cart').popover('dispose');
                    debugger
                    return _super();
                }
            });

        },
});