/** @odoo-module **/
/* global Stripe */

import { rpc, RPCError } from "@web/core/network/rpc";
import { loadJS } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { StripeOptions } from '@payment_stripe/js/stripe_options';
import PaymentForm from '@payment/js/payment_form';
PaymentForm.include({


    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'stripe') {
            this._super(...arguments);
            return;
        }



        // Check if instantiation of the element is needed.
        this.stripeElements ??= {}; // Store the element of each instantiated payment method.
        // Check if instantiation of the element is needed.
        if (flow === 'token') {
            return; // No elements for tokens.
        } else if (this.stripeElements[paymentOptionId]) {
            this._setPaymentFlow('direct'); // Overwrite the flow even if no re-instantiation.
            return; // Don't re-instantiate if already done for this provider.
        }
        // Extract and deserialize the inline form values.
        const radio = document.querySelector('input[name="o_payment_radio"]:checked');
        const inlineForm = this._getInlineForm(radio);
        const stripeInlineForm = inlineForm.querySelector('[name="o_stripe_element_container"]');
        this.stripeInlineFormValues = JSON.parse(
            stripeInlineForm.dataset['stripeInlineFormValues']
        );
        if (!(this.stripeInlineFormValues['enable_monthly_installment']) ) {
            this._super(...arguments);
            return;
        }

        // Overwrite the flow of the select payment option.
        this._setPaymentFlow('direct');

        // Instantiate Stripe object if needed.
        this.stripeJS ??= Stripe(
            this.stripeInlineFormValues['publishable_key'],
            // The values required by Stripe Connect are inserted into the dataset.
            new StripeOptions()._prepareStripeOptions(stripeInlineForm.dataset),
        );

        // Instantiate the elements.
        let elementsOptions =  {
            appearance: { theme: 'stripe' },
            currency: this.stripeInlineFormValues['currency_name'],
            captureMethod: this.stripeInlineFormValues['capture_method'],
            paymentMethodCreation: 'manual',
            paymentMethodTypes: [
                this.stripeInlineFormValues['payment_methods_mapping'][paymentMethodCode]
                ?? paymentMethodCode
            ],
        };
        if (this.paymentContext['mode'] === 'payment') {
            elementsOptions.mode = 'payment';
            elementsOptions.amount = parseInt(this.stripeInlineFormValues['minor_amount']);
            if (this.stripeInlineFormValues['is_tokenization_required']) {
                elementsOptions.setupFutureUsage = 'off_session';
            }
        }
        else {
            elementsOptions.mode = 'setup';
            elementsOptions.setupFutureUsage = 'off_session';
        }
        this.stripeElements[paymentOptionId] = this.stripeJS.elements(elementsOptions);

        // Instantiate the payment element.
        const paymentElementOptions = {
            defaultValues: {
                billingDetails: this.stripeInlineFormValues['billing_details'],
            },
        };
        const paymentElement = this.stripeElements[paymentOptionId].create(
            'payment', paymentElementOptions
        );
        paymentElement.on('loaderror', response => {
            this._displayErrorDialog(_t("Cannot display the payment form"), response.error.message);
        });
        paymentElement.mount(stripeInlineForm);

        const tokenizationCheckbox = inlineForm.querySelector(
            'input[name="o_payment_tokenize_checkbox"]'
        );
        if (tokenizationCheckbox) {
            // Display tokenization-specific inputs when the tokenization checkbox is checked.
            this.stripeElements[paymentOptionId].update({
                setupFutureUsage: tokenizationCheckbox.checked ? 'off_session' : null,
            }); // Force sync the states of the API and the checkbox in case they were inconsistent.
            tokenizationCheckbox.addEventListener('input', () => {
                this.stripeElements[paymentOptionId].update({
                    setupFutureUsage: tokenizationCheckbox.checked ? 'off_session' : null,
                });
            });
        }
    },


    async _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'stripe' || flow === 'token') {
            await this._super(...arguments); // Tokens are handled by the generic flow.
            return;
        }

        // Trigger form validation and wallet collection.

        const _super = this._super.bind(this);
        if (paymentMethodCode == 'card' && this.paymentContext['haveInstallment'] == "True"){
              try {
                await this.stripeElements[paymentOptionId].submit();
                debugger
                var payment_method = false
                    await this.stripeJS.createPaymentMethod({
                                elements:this.stripeElements[paymentOptionId],
                                params:{
                                    billing_details:JSON.parse(this._getInlineForm(document.querySelector('input[name="o_payment_radio"]:checked'))
                                    .querySelector('[name="o_stripe_element_container"]').dataset['stripeInlineFormValues'])['billing_details']
                                }
                              }).then(function(result) {
                                    payment_method = result
                              });
                    if(payment_method){
                        Object.assign(this.paymentContext, {
                                payment_method_created: payment_method['paymentMethod']['id'],
                        })
                    }

            } catch (error) {
                this._displayErrorDialog(_t("Incorrect payment details"), error.message);
                this._enableButton();
                return
            }
        }
        else{
            await this._super(...arguments);
            return;
        }

        await rpc(
            this.paymentContext['transactionRoute'],
            this._prepareTransactionRouteParams(),
        ).then(processingValues => {
            if (flow === 'redirect') {
                this._processRedirectFlow(
                    providerCode, paymentOptionId, paymentMethodCode, processingValues
                );
            } else if (flow === 'direct') {
                this._processDirectFlow(
                    providerCode, paymentOptionId, paymentMethodCode, processingValues
                );
            } else if (flow === 'token') {
                this._processTokenFlow(
                    providerCode, paymentOptionId, paymentMethodCode, processingValues
                );
            }
        }).catch(error => {
            if (error instanceof RPCError) {
                this._displayErrorDialog(_t("Payment processing failed"), error.data.message);
                this._enableButton(); // The button has been disabled before initiating the flow.
            }
            return Promise.reject(error);
        });
    },


    _prepareTransactionRouteParams() {
        const transactionRouteParams = this._super(...arguments);
        if (this.paymentContext['payment_method_created'] && this.paymentContext['haveInstallment'] == "True"){
            return {
                ...transactionRouteParams,
                'payment_method_created': this.paymentContext['payment_method_created']
            };
        }
        return {
            ...transactionRouteParams,
        };


    },

     async _stripeConfirmIntent(processingValues, paymentOptionId) {
        const _super = this._super.bind(this);
        var error = false
        var months = false
        if (this.paymentContext['haveInstallment'] == "True"){
            const txoptions = this._prepareTransactionRouteParams(this.paymentContext.providerId)
            txoptions.currency_id = parseInt(this.paymentContext.currencyId);
            txoptions.partner_id = parseInt(this.paymentContext.partnerId);
            txoptions.reference_prefix = this.paymentContext['referencePrefix']?.toString();

             await rpc("/setu_payment_acqirers/get_installment_plan", txoptions)
             .then(res=>{
                if (res.success) {
                    if (res.month) {
                        months = res.month
                    }
                }
                else if (res.error) {
                    error = res
                }
            });
        }
        if(months){
                const confirmOptions = {
                    elements: this.stripeElements[paymentOptionId],
                    clientSecret: processingValues['client_secret'],
                    confirmParams: {
                        return_url: processingValues['return_url'],
                            payment_method_options:{
                            card: {
                                installments: {
                        //                                    enabled: true,
                                    plan: {
                                        type: 'fixed_count',
                                        interval: 'month',
                                        count:months,
                                    }
                                }
                            }
                       },
                    },

                };
                if (this.paymentContext['mode'] === 'payment'){
                     return await this.stripeJS.confirmPayment(confirmOptions);
                }
                else {
                    return await this.stripeJS.confirmSetup(confirmOptions);
                }
          }
        else{
            if(error){
                   return error
            }
            else{
                return await _super(...arguments);
            }
         }
     }

});

