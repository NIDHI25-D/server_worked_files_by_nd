/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { Meter as BaseMeter } from "@auth_password_policy/password_meter";

patch(BaseMeter.prototype, {
    async setup() {
        if (super.setup) super.setup();

        // Fetch company policy dynamically from backend
        this.companyPolicy = {};
        try {
            this.companyPolicy = await rpc("/password/company_policy", {});
        } catch (err) {
            console.error("Could not fetch company policy", err);
        }

        // Reference password input
        if (!this.props.passwordNode) {
            this.props.passwordNode = document.querySelector("input[name='password']");
        }

        // Listen for password input changes
        if (this.props.passwordNode) {
            this.props.passwordNode.addEventListener("input", (ev) => {
                this.props.password = ev.target.value;
                if (this.render) this.render();
                this._toggleSubmitButton();
            });
        }

        // Reference to warning box
        this.warningBox = document.querySelector("#password_warning_box");
        this._updateWarningBox();
    },

    get value() {
        const password = this.props.password || "";
        const { passed, checks } = this._evaluatePassword(password);
        return checks === 0 ? 0 : passed / checks;
    },

    get title() {
        const policy = this.companyPolicy || {};
        const msgs = [];
        if ($('html').attr('lang')== "es-MX") {
            // Spanish messages
            if (policy.password_lower) msgs.push(`Al menos ${policy.password_lower} letra minúscula`);
            if (policy.password_upper) msgs.push(`Al menos ${policy.password_upper} letra mayúscula`);
            if (policy.password_numeric) msgs.push(`Al menos ${policy.password_numeric} número`);
            if (policy.password_special) msgs.push(`Al menos ${policy.password_special} carácter especial`);
            if (policy.password_minlength) msgs.push(`Al menos ${policy.password_minlength} caracteres`);
        } else {
            // Default English messages
            if (policy.password_lower) msgs.push(`At least ${policy.password_lower} lowercase letter(s)`);
            if (policy.password_upper) msgs.push(`At least ${policy.password_upper} uppercase letter(s)`);
            if (policy.password_numeric) msgs.push(`At least ${policy.password_numeric} number(s)`);
            if (policy.password_special) msgs.push(`At least ${policy.password_special} special character(s)`);
            if (policy.password_minlength) msgs.push(`At least ${policy.password_minlength} characters long`);
        }


        return msgs.join(", ");
    },

    _toggleSubmitButton() {
        const submitBtn = document.querySelector("#reset_password_submit");
        if (!submitBtn) return;

        const password = this.props.password || "";
        const { passed, checks } = this._evaluatePassword(password);
        const allValid = checks > 0 && passed === checks;

        submitBtn.classList.toggle("d-none", !allValid);

        // Show/hide warning box
        if (this.warningBox) {
            this.warningBox.style.display = allValid ? "none" : "block";
        }
    },

    _evaluatePassword(password) {
        const policy = this.companyPolicy || {};
        let checks = 0;
        let passed = 0;

        if (policy.password_lower) {
            checks++;
            if ((password.match(/[a-z]/g) || []).length >= policy.password_lower) passed++;
        }
        if (policy.password_upper) {
            checks++;
            if ((password.match(/[A-Z]/g) || []).length >= policy.password_upper) passed++;
        }
        if (policy.password_numeric) {
            checks++;
            if ((password.match(/[0-9]/g) || []).length >= policy.password_numeric) passed++;
        }
        if (policy.password_special) {
            checks++;
            if ((password.match(/[^A-Za-z0-9]/g) || []).length >= policy.password_special) passed++;
        }
        if (policy.password_minlength) {
            checks++;
            if (password.length >= policy.password_minlength) passed++;
        }

        return { passed, checks };
    },

    _updateWarningBox() {
        if (!this.warningBox) return;

        const policy = this.companyPolicy || {};
        const msgs = [];

        if ($('html').attr('lang')== "es-MX") {
            // Spanish messages
            if (policy.password_lower) msgs.push(`Al menos ${policy.password_lower} letra minúscula`);
            if (policy.password_upper) msgs.push(`Al menos ${policy.password_upper} letra mayúscula`);
            if (policy.password_numeric) msgs.push(`Al menos ${policy.password_numeric} número`);
            if (policy.password_special) msgs.push(`Al menos ${policy.password_special} carácter especial`);
            if (policy.password_minlength) msgs.push(`Al menos ${policy.password_minlength} caracteres`);
        } else {
            // Default English messages
            if (policy.password_lower) msgs.push(`At least ${policy.password_lower} lowercase letter(s)`);
            if (policy.password_upper) msgs.push(`At least ${policy.password_upper} uppercase letter(s)`);
            if (policy.password_numeric) msgs.push(`At least ${policy.password_numeric} number(s)`);
            if (policy.password_special) msgs.push(`At least ${policy.password_special} special character(s)`);
            if (policy.password_minlength) msgs.push(`At least ${policy.password_minlength} characters long`);
        }


        this.warningBox.innerHTML = msgs.join("<br>");
        this.warningBox.style.display = "block"; // Show warning by default
    },
}, "password_security_meter");
