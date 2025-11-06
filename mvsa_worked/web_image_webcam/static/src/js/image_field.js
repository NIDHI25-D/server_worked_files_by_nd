debugger
/** @odoo-module **/

import { ImageField } from "@web/views/fields/image/image_field";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import WebcamDialog from '@web_image_webcam/js/webcam_dialog';

patch(ImageField.prototype, {
    setup() {
        debugger
        super.setup(...arguments);
        this.dialogService = useService("dialog");
    },

    _openRearCamera(ev) {
        debugger
        this.dialogService.add(WebcamDialog, {
            mode: true,
            onWebcamCallback: (data) => this.onWebcamCallback(data),
        });
    },

    async onWebcamCallback(base64) {
        debugger
        const record = this.props.record;
        const { save } = Object.assign({ save: false }, {});
        await record.update({ [this.props.name]:  base64 });
        if (record.selected && record.model.multiEdit) {
            return;
        }
        const rootRecord =
            record.model.root instanceof record.constructor && record.model.root;
        const isInEdition = rootRecord ? rootRecord.isInEdition : record.isInEdition;
        if ((!isInEdition && !readonlyFromModifiers) || save) {
            // TODO: maybe move this in the model
            return record.save();
        }
    }

});