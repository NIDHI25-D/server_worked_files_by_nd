/** @odoo-module **/
//debugger
import publicWidget from "@web/legacy/js/public/public_widget";
import { _t } from "@web/core/l10n/translation";
publicWidget.registry.WebsiteSaleCheckout = publicWidget.registry.WebsiteSaleCheckout.extend({
//    async _updateDeliveryMethod(radio) {
//
//    this._super.apply(this, arguments);
//        const result = await this._setDeliveryMethod(radio.dataset.dmId);
//        this._updateMsgOnWebsite(radio, result)
//
//        },
//
//
//    _updateMsgOnWebsite(radio, rateData) {
////    debugger
//    const deliverymsg = this._getDeliveryMsg(radio);
//    if (rateData.success) {
//         if (rateData.is_free_delivery) {
//             deliverymsg.textContent = rateData.display_msg_on_web;
//         }
//         this._toggleDeliveryMethodRadio(radio);
//    }
//},
//
//    _getDeliveryMsg(radio){
//        const deliveryMethodContainer = this._getDeliveryMethodContainer(radio);
//        return deliveryMethodContainer.querySelector('.cols');
//    },


//Task: Error displaying message on website { https://app.clickup.com/t/86dx4mc06}
//purpose : to show display_msg_on_web instead of free
        _updateAmountBadge(radio, rateData) {
            const deliveryPriceBadge = this._getDeliveryPriceBadge(radio);
            this._super.apply(this, arguments);
            if (rateData.success && rateData.is_free_delivery) {
                deliveryPriceBadge.textContent = rateData.display_msg_on_web;
            }
        },

});
