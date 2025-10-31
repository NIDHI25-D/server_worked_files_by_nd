/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Numpad } from "@point_of_sale/app/generic_components/numpad/numpad";

patch(Numpad.prototype, {
    get buttons() {
        const originalButtons = super.buttons;

        return originalButtons.map(button => {
            if (button.value === "."|| button.value === "-") {
                return {
                    ...button,
                    disabled: true
                };
            }
            return button;
        });
    }
});
