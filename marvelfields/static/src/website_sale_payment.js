/** @odoo-module **/

import { renderToMarkup } from '@web/core/utils/render';
import paymentForm from '@payment/js/payment_form';

paymentForm.include({
    _prepareTransactionRouteParams(providerId) {
        debugger
        const transactionRouteParams = this._super(...arguments);
        const partner_bill = document.querySelector('input[name="o_partner_bill"]');
        if (partner_bill){
            return {
                ...transactionRouteParams,
                'is_billing_general': partner_bill.checked
            };
        }
        return {
            ...transactionRouteParams,
        };
    },
});