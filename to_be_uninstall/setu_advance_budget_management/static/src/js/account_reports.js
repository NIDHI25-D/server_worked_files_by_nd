odoo.define('setu_advance_budget_management.account_reports', function (require) {
'use strict';

var core = require('web.core');
var BudgetAbstractAction = require('account_reports.account_report');
var Widget = require('web.Widget');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var { WarningDialog } = require("@web/legacy/js/_deprecated/crash_manager_warning_dialog");
var Widget = require('web.Widget');

var _t = core._t;

 BudgetAbstractAction.accountReportsWidget.include({
        render_searchview_buttons: function() {
        var self = this;
            this.$searchview_buttons.find('.js_account_report_date_cmp_filter').bind( "click",function (event) {
                     var budget_id = $(this).parent().find('select[name="budget_id"]');
                     self.report_options.comparison.budget_id = (budget_id.length > 0) ? parseInt(budget_id.val()) : false;
            })
        this._super.apply(this, arguments);
        }
        });
 });