/** @odoo-module **/

import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(BarcodeModel.prototype, {
// task: Error in the put in back button with partialities , url: https://app.clickup.com/t/86dx9vdz5
// as per task remove this code
//    async _createNewLine(params) {
//    if (this.record.picking_type_code === 'incoming')
//        return super._createNewLine(params);
//    },

    get groupedLinesByLocation() {
        const lines = [].concat(this.groupedLines, this.packageLines);
        const linesByLocations = []
        const linesByLocation = {};
        for (const line of lines) {
            const lineLoc = line.location_id;
            if (!linesByLocation[lineLoc.id]) {
                linesByLocation[lineLoc.id] = {
                    location: lineLoc,
                    lines: [],
                };
            }
            if (!linesByLocations.includes(linesByLocation[lineLoc.id])) {
                linesByLocations.push(linesByLocation[lineLoc.id]);
            }
            linesByLocation[lineLoc.id].lines.push(line);
        }
        // Sorts groups to ensure that locations will always follow the alphabetical order.
        linesByLocations.sort((lblA, lblB) => {
            const [locNameA, locNameB] = [lblA.location.display_name, lblB.location.display_name];
            return locNameA < locNameB ? 1 : locNameA > locNameB ? -1 : 0; // Sort by source location. [ Z --- A ]
        });
        return linesByLocations
    }
});
