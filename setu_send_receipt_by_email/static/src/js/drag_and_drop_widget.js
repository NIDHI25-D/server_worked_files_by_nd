/** @odoo-module **/

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";

export class DragAndDropWidget extends Component {
    "use strict";
    static template = "setu_send_receipt_by_email.DragAndDropWidgetTemplate"

    setup() {
        super.setup();
        this.files = {};
        this.uploading_files = false;
        this.action = useService("action");
        this.actionService = useService('action');
        this.orm = useService('orm');
        this.ui = useService("ui");

        this.setupEventListeners();
    }

    setupEventListeners() {
        const handler = this;

        $(this.el).on('dragenter dragover', function (e) {
            e.stopPropagation();
            e.preventDefault();
            handler.updateDragState(true);
        });

        $(this.el).on('drop', function (e) {
            e.stopPropagation();
            e.preventDefault();
            handler.updateDragState(false);
            handler._onDragDropfn(e);
        });

        $(this.el).on('dragleave', function (e) {
            e.stopPropagation();
            e.preventDefault();
            handler.updateDragState(false);
        });
    }

    updateDragState(isDragging) {
        const dropArea = $(this.el);
        if (isDragging) {
            dropArea.removeClass('dnd_normal').addClass('dnd_out');
        } else {
            dropArea.removeClass('dnd_out').addClass('dnd_normal');
        }
    }

    _onDragClickfn(e) {
        $(this).find("#files").val("");
        $(this).find("#files").click();
    }

    _onFilesChange(e) {
        console.log("files Change")
    }

    _onDragDropfn(e) {
    if (this.props.record.data.receipt_status === 'sent') return;
        this.fileUpload(e.dataTransfer.files);
    }

    fileUpload(files) {
        const allowedFileTypes = ['image/jpeg', 'text/html', 'application/pdf', 'image/png'];

        if (this.uploading_files) {
            this.files = {};
        }

        this.uploading_files = true;

        $.each(files, (i, file) => {
            if (allowedFileTypes.includes(file.type)) {
                this.files[file.name] = file;
                this.readFile(file);
            } else {
                debugger
                this.env.model.notification.add(
                    _t(`Invalid file type: ${file.name}`),
                    { type: "warning" }
                );
                this.uploading_files = false;
            }
        });
    }

    readFile(file) {
    debugger
        const reader = new FileReader();
        reader.onload = (e) => {
            const base64Data = e.target.result.split(',')[1];
            const fileName = file.name;
            this.saveFile(base64Data, fileName);
        };
        reader.readAsDataURL(file);
    }

    async saveFile(base64Data, fileName) {
    debugger
    const recordId = this.props.record.data.id;
    const modelName = this.props.record.resModel;

    if (!recordId) {
        console.error("Invalid recordId:", recordId);
        this.uploading_files = false;
        return;
    }

        this.ui.block();

    try {
        await this.orm.call(modelName, 'write', [[recordId], {vendor_payment_receipt: base64Data, vendor_payment_receipt_name: fileName}]);
        this.uploading_files = false;
        this.files = {};
        this.env.model.notification.add(
            _t("File uploaded successfully"),
            { type: "success" }
        );
        debugger
        this.ui.unblock();
    } catch (error) {
        this.uploading_files = false;
        this.env.model.notification.add(
            _t("Error uploading file: ") + (error.message || 'Unknown error'),
            { type: "danger" }
        );
        this.ui.unblock();
    }
}

};

export const dragAndDropWidget = {
    component: DragAndDropWidget,
    displayName: _t("File Upload"),
    supportedTypes: ["binary"],
};

registry.category("fields").add('drag_and_drop_widget', dragAndDropWidget);