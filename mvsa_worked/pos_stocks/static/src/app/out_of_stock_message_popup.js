const { Component, useRef, useState } = owl;
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";

export class OutOfStockMessagePopup extends Component {
    static components = { Dialog };
    static props = {
        title: String,
        body: String,
        close: Function,
    };
    static template = "OutOfStockMessagePopup";
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
    }

    closePopup() {
        this.props.close();
    }
}
