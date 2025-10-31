import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { rpc, RPCError } from "@web/core/network/rpc";
import PaymentForm from '@payment/js/payment_form';
PaymentForm.include({
      async _expandInlineForm(radio) {
            var res = this._super.apply(this, arguments)
            $("input[name='website_order_partner_name']").prop('placeholder', _t("Cardholder's name as it appears on the card"))
            var self = this;
            if($("input[name='mercado_pago_public_key']").val()){
                self.mp = new MercadoPago($("input[name='mercado_pago_public_key']").val());
                const cardNumberElement = self.mp.fields.create('cardNumber', {
                    placeholder: _t("Card Number"),
                    style: {
                        height: "25px"
                    },
                }).mount('form-checkout__cardNumber');
                const expirationDateElement = self.mp.fields.create('expirationDate', {
                    placeholder: "MM/YY",
                    style: {
                        height: "25px",
                        width:"150px"
                    },
                }).mount('form-checkout__expirationDate');
                const securityCodeElement = self.mp.fields.create('securityCode', {
                    placeholder: _t("Security Code"),
                    style: {
                        height: "25px",
                        width:"160px"
                    },
                }).mount('form-checkout__securityCode');
                let currentBin;
                cardNumberElement.on('binChange', async(data) => {
                    this.$el.find('#payment_error').remove()
                    const { bin } = data
                    var card_type = $.payment.cardType(bin);
                    if (card_type) {
                        this.$el.find(".card_placeholder").removeClass().addClass('card_placeholder ' + card_type);
                        this.$el.find("input[name='cc_brand']").val(card_type)
                    }
                    else {
                        this.$el.find(".card_placeholder").removeClass().addClass('card_placeholder');
                    }
                        currentBin = bin;
                });
            }

            return res
        },
      async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
            if (providerCode !== 'mercado_pago') {
                return this._super(...arguments);
            }
            if (flow === 'token') {
                return Promise.resolve(); // Don't show the form for tokens
            }

            this._setPaymentFlow('direct');

            let acceptJSUrl = 'https://sdk.mercadopago.com/js/v2/';
              return rpc('/payment/mercado_pago/get_provider_info',  {
               'provider_id': providerId,
            }).then(providerInfo => {
                acceptJSUrl = 'https://sdk.mercadopago.com/js/v2/';
                this.authorizeInfo = providerInfo;
            }).then(() => {
                loadJS(acceptJSUrl);
            }).catch((error) => {
//                var errorStr="";
//                 $.each(error, function(i,v){
//                    errorStr +=v.message+"."
//                })
                this._displayErrorDialog(
                    _t("Server Error"),
                    _t("An error occurred when displayed this payment form. \n"+ error)
                );
                 self._enableButton();
            });
        },

      async createToken(providerId){
            self=this;
            card_holder_name = ""
            var card_holder_name = $("input[name='website_order_partner_name']").val()
            self.token = await self.mp.fields.createCardToken({
                cardholderName : card_holder_name
            })
            await self.mp.getPaymentMethods({"bin":self.token.first_six_digits}, function (status, response) {
                console.log(response)
            }).then(function(data) {
                self.payment_methods_data = data
                console.log(data)
                  rpc(self.paymentContext.transactionRoute,
                   self._prepareTransactionRouteParams('mercado_pago', providerId, 'direct')
                ).then(processingValues => {
                        rpc('/payment/mercado_pago/payment', {
                            'reference': processingValues.reference,
                            'partner_id': processingValues.partner_id,
                            'provider_id':processingValues.provider_id,
                            'mp_payment_token':self.token,
                            'mp_payment_method_data':self.payment_methods_data,
                            'website_order_partner_name':card_holder_name,
                            'tokenization_request_allowed':self.paymentContext.tokenizationRequested,
                    }).then(function(data) {
                        if (data.error) {
                                self._displayErrorDialog('',_t(data.error));
                                self._enableButton();
                         }
                         // if the server has returned true
                        else if (data.result) {
                               window.location = '/payment/status'
                        }
                        // if the server has returned false, we display an error
                        else {
                             // if the server doesn't provide an error message
                                self._displayErrorDialog(
                                    _t('Server Error'),
                                    _t('e.g. Your credit card details are wrong. Please verify.'));
                                self._enableButton();
                        }
                    })
                })
            })
        },

      async _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {


            if (providerCode !== 'mercado_pago' || flow === 'token') {
                return this._super(...arguments); // Tokens are handled by the generic flow
            }

            this.createToken(paymentOptionId).catch(function (error) {
//                var errorStr="";
//                 $.each(error, function(i,v){
//                    errorStr +=v.message+" "
//                })
                self._displayErrorDialog(
                    _t('Server Error'),
                    _t("We are not able to add your payment method at the moment. \n" + error));
                self._enableButton();

            })

        },

//    };
//
//    checkoutForm.include(mercadopagoMixin);
//    manageForm.include(mercadopagoMixin);

});