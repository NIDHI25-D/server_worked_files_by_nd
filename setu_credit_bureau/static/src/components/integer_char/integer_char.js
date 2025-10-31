/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useInputField } from "@web/views/fields/input_field_hook";
import { Component, useState } from "@odoo/owl";
import { useNumpadDecimal } from "@web/views/fields/numpad_decimal_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { parseInteger } from "@web/views/fields/parsers";
import { _t } from "@web/core/l10n/translation";


export class ValidValues extends Component {
    static template = "setu_credit_bureau.ValidValues";
    static props = {
    ...standardFieldProps,
    inputType: { type: String, optional: true },
    step: { type: Number, optional: true },
    placeholder: { type: String, optional: true },
    maxLength: { type: Number, optional: true },
};
    static defaultProps = {
    inputType: "text",
};

    setup() {
        this.state = useState({
            hasFocus: false,
        });
        useInputField({
            getValue: () => this.value,
            refName: "inputNumber",
            parse: (v) => this.parseNumericInput(v),
        });
        useNumpadDecimal();

    }


    parseNumericInput(value) {
    debugger
        if (!value) return "";
        let numericValue = value.replace(/\D/g, "");
        if (numericValue !== value) {
            this.notification.add();
        }

        if (this.props.maxLength && numericValue.length > this.props.maxLength) {
            this.notification.add();
            numericValue = numericValue.substring(0, this.props.maxLength);
        }

        return numericValue;
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

}

export const validValuesField = {
    component: ValidValues,
    displayName: _t("Char"),
    supportedTypes: ["char"],
    isEmpty: (record, fieldName) => !record.data[fieldName],
    extractProps: ({ field }) => ({
        maxLength: field.size,
    }),
};

registry.category("fields").add("valid_char", validValuesField);