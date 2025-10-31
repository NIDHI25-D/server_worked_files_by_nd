/** @odoo-module **/

import MainComponent from '@stock_barcode/components/main';
import {_t, _lt} from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(MainComponent.prototype, {

    setup() {
        super.setup();
    },

    putInPack(ev) {
        debugger
        const context = ev.currentTarget.getAttribute('context')
            if (context){
                const additionalContext = { massive_package: true }
               return this.env.model._putInPack(additionalContext);
            }
            else{
            const additionalContext = {}
            return this.env.model._putInPack(additionalContext); }
        }
});

//
//patch(BarcodePickingModel.prototype, 'setu_picking_control_by_pallets', {
//     async _putInPack(additionalContext) {
//        debugger
//        const context = Object.assign({ massive_package: true }, additionalContext);
//        debugger
//        return this._super(additionalContext);
//    }
//});
