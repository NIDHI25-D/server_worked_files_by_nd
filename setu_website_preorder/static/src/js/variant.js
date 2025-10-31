/** @odoo-module **/

import VariantMixin from "@website_sale_stock/js/variant_mixin";
import { WebsiteSale } from '@website_sale/js/website_sale';
import { renderToMarkup } from "@web/core/utils/render";
import wSaleUtils from "@website_sale/js/website_sale_utils";
import { PreorderProductsInformation } from "@setu_website_preorder/app/preorder_product_info";
import { rpc } from "@web/core/network/rpc";
import { Component } from "@odoo/owl";


import { markup } from "@odoo/owl";
import { renderToFragment } from "@web/core/utils/render";

const oldChangeCombinationStock = VariantMixin._onChangeCombinationStock;

$(window).ready(function(){
    window.localStorage.removeItem('stock_type');
    window.localStorage.setItem('is_exclusive','False')
        if (window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
        window.localStorage.removeItem('stock_type');
        window.localStorage.setItem('is_exclusive','False')
    }
})
//task: Add product pre-sale to the cart {https://app.clickup.com/t/86dxxgcw7}
//made async because base method is async

VariantMixin._onChangeCombinationStock = async function (ev, $parent, combination) {
//    debugger
    $('div#presale_content').html('')
    $('div#preorder_content').html('')
    $("div#prevent_stock").remove()
    $("div#buy_it_as_div").css('display', 'none')

    const $addQtyInput = $parent.find('input[name="add_qty"]');
    const $custom_price_message = $parent.find('span[class="price_message"]')[0]
    this.stock_type = window.localStorage.getItem('stock_type');
    var old_value = parseInt($addQtyInput.val() || 1)
    const ctxWrapper = $("#o_wsale_cta_wrapper")[0]
    await oldChangeCombinationStock.apply(this, arguments);
    if (combination.order_type && !this.stock_type){
        this.stock_type = combination.order_type
        window.localStorage.setItem('stock_type', combination.order_type);
    }
//    debugger
    $('.availability_messages').html(
        renderToFragment('website_sale_stock.product_availability', combination)
    );
//    debugger
    $('div#preorder_content').html(renderToMarkup('preorderProductsInformation', combination))

    setTimeout(() => {
    const el = document.getElementById('preorder_note_message');
    if (el && combination.presale_qty) {
        el.innerHTML = combination.website_presale_msg;
    }
    if (el && combination.international_preorder_qty) {
        el.innerHTML = combination.intl_preorder_msg;
    }
        }, 0);

    $('div#exclusivity_procedure').html(renderToMarkup('exclusive_preorder_information', combination))
    $("div#buy_it_as_div").css('display', 'block')
    var stock_values =$("select#buy_it_as").children().map((c,d) => d.value).toArray()
//    debugger
    $("div#buy_it_as_div").css('display', 'none')
    if (combination.is_preorder) {
        $addQtyInput.data('max', combination.preorder_qty || 1);
        $addQtyInput.val(old_value)
        if ($("select#buy_it_as").val() == 'preorder'){
            $addQtyInput.data('min', combination.minimum_qty_for_preorder_presale);
            if (!($addQtyInput.val() >=combination.minimum_qty_for_preorder_presale)){
                $addQtyInput.val(combination.minimum_qty_for_preorder_presale)
            }
            window.localStorage.setItem('stock_type', 'preorder');
        }
        if (combination.order_type === 'preorder' || combination.order_type === '') {
            ctxWrapper.classList.replace('d-none', 'd-flex')
        } else {
            $('#prevent_stock').removeClass('d-none')
        }
    }

    if (combination.is_presale && combination.presale_price > 0) {
//    debugger
        $addQtyInput.data('max', combination.presale_qty || 1);
        $addQtyInput.val(old_value)
        if ($("select#buy_it_as").val() == 'presale'){
            $addQtyInput.data('min', combination.minimum_qty_for_preorder_presale);
            $('.presale_price_tag').removeClass('d-none')
            if (!($addQtyInput.val() >=combination.minimum_qty_for_preorder_presale)){
                $addQtyInput.val(combination.minimum_qty_for_preorder_presale)
            }
            window.localStorage.setItem('stock_type', 'presale');
        }
        if (combination.order_type === 'presale' || combination.order_type === '') {
            ctxWrapper.classList.replace('d-none', 'd-flex')
        } else {
            $('#prevent_stock').removeClass('d-none')
        }
    }
    if (combination.is_international_pre_order_product){
        if ($('html').attr('lang')== "es-MX")
        {
            $custom_price_message.innerText = 'Precio'
        }
        if ($('html').attr('lang')== "en-US")
        {
            $custom_price_message.innerText = 'Price'
        }
        $addQtyInput.data('max', combination.international_preorder_qty || 1);
        $addQtyInput.val(old_value)
        if ($("select#buy_it_as").val() == 'international_preorder'){
            // Exclusive boolean is displayed as per the condition
            if (combination.minimum_exclusivity_quantity <= combination.international_preorder_qty)
            {
                $('.exclusivity_product').removeClass('d-none')
            }
            if (!($addQtyInput.val() >=combination.minimum_qty_for_preorder_presale)){
                $addQtyInput.val(combination.minimum_qty_for_preorder_presale)
            }
            if (window.localStorage.getItem('is_exclusive') == 'True'){
                var checkbox = document.getElementById("international_exclusivity");
                checkbox.setAttribute('checked',1)
                if(!($addQtyInput.val() >=combination.minimum_exclusivity_quantity))
                {
                    $addQtyInput.val(combination.minimum_exclusivity_quantity)
                }
            }
            window.localStorage.setItem('stock_type', 'international_preorder');
        }
        if (combination.order_type === 'international_preorder' || combination.order_type === '') {
            ctxWrapper.classList.replace('d-none', 'd-flex')
        } else {
            $('#prevent_stock').removeClass('d-none')
        }
    }
    else{
        $('.exclusivity_product').addClass('d-none')
    }
//    debugger
    if (combination.is_next_day_shipping && combination.free_qty > 0 ) {
        if ($("select#buy_it_as").val() == 'is_next_day_shipping'){
           window.localStorage.setItem('stock_type', 'is_next_day_shipping');
        }
        if (combination.order_type === 'is_next_day_shipping' || combination.order_type === '') {
                ctxWrapper.classList.replace('d-none', 'd-flex')
        }
        else if (combination.order_type === 'stock'){
                ctxWrapper.classList.replace('d-none','d-flex')
                $('#next_day_shipping_alert').removeClass('d-none')
        }
        else {
                $('#prevent_stock').removeClass('d-none')
            }
    }
    if (combination.order_type !== '' && combination.order_type !== 'stock' && combination.free_qty > 0 && !(combination.is_preorder || combination.is_presale || combination.is_international_pre_order_product || combination.is_next_day_shipping)) {
        ctxWrapper.classList.replace('d-flex', 'd-none')
        $('#prevent_stock').removeClass('d-none')
    }

    if (combination['free_qty'] > 0 && (combination.is_presale || combination.is_preorder || combination.is_international_pre_order_product || combination.is_next_day_shipping)) {
//    debugger
        if ((combination.order_type =='' && this.stock_type == undefined) || (stock_values.includes(combination.order_type) || stock_values.includes(this.stock_type))){
//        debugger
            $("div#prevent_stock").remove()
            $("div#buy_it_as_div").css('display', 'block')
            if (combination.order_type) {
                $("select#buy_it_as").val(combination.order_type)
                if ($("select#buy_it_as").val() == 'preorder' || $("select#buy_it_as").val() == 'presale'){
                    if($("select#buy_it_as").val() == 'presale'){
                        $('.oe_presale_price').removeClass('d-none')
                        }
                    $('input[name="add_qty"]').data('min',combination.minimum_qty_for_preorder_presale);
                if (!($('input[name="add_qty"]' ).val() >= combination.minimum_qty_for_preorder_presale)){
                    $('input[name="add_qty"]' ).val(combination.minimum_qty_for_preorder_presale)
                    }
                }
                $("select#buy_it_as").attr('disabled', 1)
            } else if (this.stock_type && combination.order_type !='') {
                $("select#buy_it_as").attr('disabled', 1)
            }
//   as there are a default base issues from combination pass  product_template_id but in template there are write like product_template hence takes as it is.
//            $('.oe_website_sale').find('.availability_message_' + combination.product_template_id).remove();
            $('.oe_website_sale').find('.availability_message_' + combination.product_template).remove();
        }else{
        $('#prevent_stock').removeClass('d-none')
            ctxWrapper.classList.replace('d-flex', 'd-none')
        }
        if ($("select#buy_it_as").val() == 'stock'){
            $addQtyInput.data('min', 1);
        }
        if(combination.is_presale && combination.presale_price > 0){
            $('.presale_price_tag').removeClass('d-none')
        }
    }
    if (combination.free_qty < 1 && (combination.is_preorder || combination.is_presale || combination.is_international_pre_order_product)) {
//        debugger
//   as there are a default base issues from combination pass  product_template_id but in template there are write like product_template hence takes as it is.
//        $('.oe_website_sale').find('.availability_message_' + combination.product_template_id).remove();
        $('.oe_website_sale').find('.availability_message_' + combination.product_template).remove();
    }
    $("select#buy_it_as").change(function (ev) {
        window.localStorage.setItem('stock_type', $(this).val());
        if ($("select#buy_it_as").val() == 'preorder' || $("select#buy_it_as").val() == 'presale'){
            $('input[name="add_qty"]').data('min',combination.minimum_qty_for_preorder_presale);
            if (!($('input[name="add_qty"]' ).val() >= combination.minimum_qty_for_preorder_presale)){
                $('input[name="add_qty"]' ).val(combination.minimum_qty_for_preorder_presale)
            }
        }
        if ($("select#buy_it_as").val() == 'presale' &&  combination.presale_price > 0){
            $('.presale_price_tag').removeClass('d-none')
        }
        if ($("select#buy_it_as").val() == 'stock'){
            $('.exclusivity_product').addClass('d-none')
            $('input[name="add_qty"]').data('min',1);
            $('input[name="add_qty"]').val(1)
        }
        if ($("select#buy_it_as").val() == 'international_preorder'){
            if (combination.minimum_exclusivity_quantity <= combination.international_preorder_qty)
            {
                $('.exclusivity_product').removeClass('d-none')
            }
        }
        if ($("select#buy_it_as").val() == 'is_next_day_shipping'){
//            debugger
            $('input[name="add_qty"]').data('min',1);
            $('input[name="add_qty"]').val(1)
        }
    }),
    $("#international_exclusivity").click(function (ev) {
        var checkbox = document.getElementById("international_exclusivity");
        if (checkbox.checked) {
            $('input[name="add_qty"]').val(combination.minimum_exclusivity_quantity);
            $('input[name="add_qty"]').data('min',combination.minimum_exclusivity_quantity);
            $("select#buy_it_as").attr('disabled', 1)
            window.localStorage.setItem('is_exclusive','True')
        }
        else if ($("select#buy_it_as").val() == 'international_preorder' && !checkbox.checked)
        {
            $("select#buy_it_as").prop('disabled',false)
            $('input[name="add_qty"]').data('min',1);
            window.localStorage.setItem('is_exclusive','False')
        }
        else
        {
            $('input[name="add_qty"]').data('min',1);
            $("select#buy_it_as").prop('disabled',false)
            window.localStorage.setItem('is_exclusive','False')
        }
    })
};



WebsiteSale.include({

    _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
//    debugger
        $($dom_optional).toArray().forEach((elem) => {
            $(elem).find('.js_quantity').text(value);
            productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
        });
        $input.data('update_change', true);
        var exclusive_line = $input.data('exclusive')
        rpc("/shop/cart/update_json", {
            line_id: line_id,
            product_id: parseInt($input.data('product-id'), 10),
            set_qty: value,
            display: true,
            is_exclusive: exclusive_line,
        }).then((data) => {
            $input.data('update_change', false);
            var check_value = parseInt($input.val() || 0, 10);
            if (isNaN(check_value)) {
                check_value = 1;
            }
            if (value !== check_value) {
                $input.trigger('change');
                return;
            }
            if (!data.cart_quantity) {
                return window.location = '/shop/cart';
            }
            $input.val(data.quantity);
            $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).text(data.quantity);

            wSaleUtils.updateCartNavBar(data);
            wSaleUtils.showWarning(data.notification_info.warning);
            // Propagating the change to the express checkout forms
            Component.env.bus.trigger('cart_amount_changed', [data.amount, data.minor_amount]);
        });
    },

    _updateRootProduct($form, productId, productTemplateId) {
//    debugger
        var res = this._super.apply(this, arguments);
        if (window.localStorage.getItem('stock_type'))
        {
            this.rootProduct.stock_type = window.localStorage.getItem('stock_type');
        }
        else
        {
            this.rootProduct.stock_type = $(".shop_buy_it_as").val()
        }
        this.rootProduct.is_exclusive = window.localStorage.getItem('is_exclusive');

        return res
    },
    handleCustomValues: function ($target) {
//        debugger
        if ($target.parent().prop('id') == 'add_to_cart' || $target.parent().prop('id')=='add_to_cart_wrap') {
            this.stock_type = window.localStorage.getItem('stock_type');
            return $.when(this._super.apply(this, arguments)).then(function(){ $("select#buy_it_as").attr('disabled', 1)});
        }
    }
})
