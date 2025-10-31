/** @odoo-module */

    import { loadJS } from "@web/core/assets";
    import { _t } from "@web/core/l10n/translation";
    import publicWidget from '@web/legacy/js/public/public_widget';
    import PaymentForm from "@payment/js/payment_form";
    import TermsAndConditionsCheckbox from "@website_sale/js/terms_and_conditions_checkbox";



    publicWidget.registry.TermsAndConditionsCheckboxSetu = publicWidget.Widget.extend({
        selector: 'div[id="understood_entendido"]',
        events: {
            'change #entendido': '_onClickEntendido',
        },
        async start() {
            const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
            var $checkboxTc = document.getElementById("website_sale_tc_checkbox");
            if ($checkedRadios.length === 1 && $checkedRadios.attr('data-provider-payment-voucher-warning'))
                {
                    $('.payment_voucher_warning_class').removeClass('d-none');
                    $('#understood_entendido').removeClass('d-none');
                    $checkboxTc.disabled = true
                }
            this._super.apply(this, arguments);
        },

        _onClickEntendido() {
            var $checkboxEntendido = document.getElementById("entendido");
            var $checkboxTc = document.getElementById("website_sale_tc_checkbox");
            const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
            const $submitButton = $('button[name="o_payment_submit_button"]');
            if ($checkboxEntendido.checked && !document.getElementById('website_sale_tc_checkbox').checked) {
                $checkboxTc.disabled = false;
                $submitButton.attr('disabled', true);
            }
            else if (!$checkboxEntendido.checked && $checkedRadios.attr('data-provider-payment-voucher-warning')){
                $checkboxTc.disabled = false;
                $submitButton.attr('disabled', true);
            }
            else if ($checkboxEntendido.checked && document.getElementById('website_sale_tc_checkbox').checked){
                $submitButton.attr('disabled', false);
            }
            else if (!$checkboxEntendido.checked && document.getElementById('website_sale_tc_checkbox').checked){
                $checkboxTc.checked = false;
                $checkboxTc.disabled = true;
                $submitButton.attr('disabled', true);
            }
            else if (!$checkboxEntendido.checked && !document.getElementById('website_sale_tc_checkbox').checked){
                $checkboxTc.checked = false;
                $checkboxTc.disabled = true;
                $submitButton.attr('disabled', true);
            }
            else{
                $submitButton.attr('disabled', true);
            }
        },
    });

    export default publicWidget.registry.TermsAndConditionsCheckboxSetu;

    PaymentForm.include({
        _selectPaymentOption(ev) {
            this._super(...arguments);
            var $checkboxTc = document.getElementById("website_sale_tc_checkbox");
            var $checkboxEntendido = document.getElementById("entendido");
            const $checkedRadios = this.$('input[name="o_payment_radio"]:checked');
            var $submitButton = $('button[name="o_payment_submit_button"]');
            if ( $(ev.currentTarget).attr('data-provider-payment-voucher-warning') && $checkboxEntendido !== null)
                    {
                        $('.payment_voucher_warning_class').removeClass('d-none');
                        $('#understood_entendido').removeClass('d-none');
                        $checkboxEntendido.checked = false;
                        $checkboxTc.checked = false;
                        $checkboxTc.disabled = true;

                    }
            else if($checkboxEntendido !== null && !$checkboxEntendido.length === 1 && $(ev.currentTarget).attr('data-provider-payment-voucher-warning'))
                {
                    $checkboxTc.disabled = false
                    $submitButton.attr('disabled', true);
                }
            else
                {
                    if ($checkboxTc !== null || $checkboxEntendido !== null){
                        $checkboxTc.disabled = false
                        $submitButton.attr('disabled', false);
                        $('.payment_voucher_warning_class').addClass('d-none');
                        $('#understood_entendido').addClass('d-none');
                    }
                }
        },
        _prepareTransactionRouteParams() {
            const transactionRouteParams = this._super(...arguments);
            var $checkboxEntendido = document.getElementById("entendido");
            var $flag_entendido = false
            if ($checkboxEntendido !== null)
            {
                $flag_entendido = true
            }
            return {
                    ...transactionRouteParams,
                    'is_payment_voucher_warning': $flag_entendido
            };
        },
    });

