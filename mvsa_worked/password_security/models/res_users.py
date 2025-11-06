# -*- coding: utf-8 -*-
import re

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


def delta_now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class ResUsers(models.Model):
    _inherit = "res.users"

    password_write_date = fields.Datetime(
        string="Last password update",
        default=fields.Datetime.now,
        readonly=True, copy=False
    )
    password_history_ids = fields.One2many(
        string="Password History",
        comodel_name="res.users.pass.history",
        inverse_name="user_id",
        readonly=True,
    )

    def write(self, vals):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: When user will change password set password date
        :param vals: 
        :return: True or False 
        """
        if vals.get("password"):
            vals["password_write_date"] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    @api.model
    def get_password_policy(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 31/01/2025
        Task: Password Security
        Purpose: This method will used to add password policy and also added new parameter when update password check some regular expression
        :return: 
        """
        data = super(ResUsers, self).get_password_policy()
        company_id = self.env.user.company_id
        data.update(
            {
                "password_lower": company_id.password_lower,
                "password_upper": company_id.password_upper,
                "password_numeric": company_id.password_numeric,
                "password_special": company_id.password_special,
            }
        )
        return data

    def _check_password_policy(self, passwords):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will used to check password policy
        :param passwords:
        :return:
        """
        result = super(ResUsers, self)._check_password_policy(passwords)
        for password in passwords:
            if not password:
                continue
            self._check_password(password)

        return result

    def password_match_message(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will prepare password match message
        :return: message
        """
        self.ensure_one()
        company_id = self.company_id
        message = []
        if company_id.password_lower:
            message.append(
                _("\n* Lowercase letter (at least %s characters)")
                % str(company_id.password_lower)
            )
        if company_id.password_upper:
            message.append(
                _("\n* Uppercase letter (at least %s characters)")
                % str(company_id.password_upper)
            )
        if company_id.password_numeric:
            message.append(
                _("\n* Numeric digit (at least %s characters)")
                % str(company_id.password_numeric)
            )
        if company_id.password_special:
            message.append(
                _("\n* Special character (at least %s characters)")
                % str(company_id.password_special)
            )
        if message:
            message = [_("Must contain the following:")] + message

        params = self.env["ir.config_parameter"].sudo()
        minlength = params.get_param("auth_password_policy.minlength", default=0)
        if minlength:
            message = [
                _("Password must be %d characters or more.") % int(minlength)
            ] + message
        return "\r".join(message)

    def _check_password(self, password):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will used to check password based on rules and history
        :param password: 
        :return: True
        """
        self._check_password_rules(password)
        self._check_password_history(password)
        return True

    def _check_password_rules(self, password):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will used to check password rule based on password configuration
        :param password:
        :return: True or validation error
        """
        self.ensure_one()
        if not password:
            return True
        company_id = self.company_id
        params = self.env["ir.config_parameter"].sudo()
        minlength = params.get_param("auth_password_policy.minlength", default=0)
        lower_string = ''.join([char for char in password if char.islower()])
        uppercase_string = ''.join([char for char in password if char.isupper()])
        special_string = ''.join([char for char in password if not char.isalnum() and not char.isspace()])
        digits = [char for char in password if char.isdigit()]
        digit_string = ''.join(digits)

        if ((len(lower_string) >= company_id.password_lower and
                len(uppercase_string) >= company_id.password_upper and
                len(digit_string) >= company_id.password_numeric) and
                len(special_string) >= company_id.password_special and
                len(password) >= int(minlength)):
            return True
        else:
            raise ValidationError(self.password_match_message())


    def _password_has_expired(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will used to check password expired or not
        :return: True or False
        """
        self.ensure_one()
        if not self.password_write_date:
            return True

        if not self.company_id.password_expiration:
            return False

        days = (fields.Datetime.now() - self.password_write_date).days
        return days > self.company_id.password_expiration

    def action_expire_password(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: Action expire password view signup page for new password
        :return:
        """
        for user in self:
            user.mapped("partner_id").signup_prepare(
                signup_type="reset",
            )

    def _validate_pass_reset(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: It provides validations before initiating a pass reset email
        :raises: UserError on invalidated pass reset attempt
        :return: True on allowed reset
        """
        for user in self:
            pass_min = user.company_id.password_minimum
            if pass_min <= 0:
                continue
            write_date = user.password_write_date
            delta = timedelta(hours=pass_min)
            if write_date + delta > datetime.now():
                raise UserError(
                    _(
                        "Passwords can only be reset every %d hour(s). "
                        "Please contact an administrator for assistance."
                    )
                    % pass_min
                )
        return True

    def _check_password_history(self, password):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: It validates proposed password against existing history
        :raises: UserError on reused password
        """
        crypt = self._crypt_context()
        for user in self:
            password_history = user.company_id.password_history
            if not password_history:  # disabled
                recent_passes = self.env["res.users.pass.history"]
            elif password_history < 0:  # unlimited
                recent_passes = user.password_history_ids
            else:
                recent_passes = user.password_history_ids[:password_history]
            if recent_passes.filtered(
                lambda r: crypt.verify(password, r.password_crypt)
            ):
                raise UserError(
                    _("Cannot use the most recent %d passwords")
                    % user.company_id.password_history
                )

    def _set_encrypted_password(self, uid, pw):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: It saves password crypt history for history rules"""
        res = super(ResUsers, self)._set_encrypted_password(uid, pw)

        self.env["res.users.pass.history"].create(
            {
                "user_id": uid,
                "password_crypt": pw,
            }
        )
        return res

    def action_reset_password(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: Disallow password resets inside of Minimum Hours"""
        if not self.env.context.get("install_mode") and not self.env.context.get(
            "create_user"
        ):
            if not self.env.user._is_admin():
                users = self.filtered(lambda user: user.active)
                users._validate_pass_reset()
        return super(ResUsers, self).action_reset_password()
