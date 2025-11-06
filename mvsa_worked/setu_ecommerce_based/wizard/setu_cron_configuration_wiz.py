# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class SetuCronConfigurationWiz(models.TransientModel):
    _name = "setu.cron.configuration.wiz"
    _description = "Cron Configuration"

    def _get_multi_ecommerce_connector(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will get ecommerce connector id from context
        :return: ecommerce connector id
        """
        return self.env.context.get('multi_ecommerce_connector_id', False)

    # Conditional fields
    order_auto_import = fields.Boolean(string='Import Order', default=False)
    stock_auto_export = fields.Boolean(string='Export Stock', default=False)
    order_status_auto_update = fields.Boolean(string="Update Order Status", default=False)

    # Integer fields
    inventory_export_interval_number = fields.Integer(string='Interval Number for Export stock')
    import_order_interval_number = fields.Integer(string='Interval Number for Import Order', help="Repeat every x.")
    order_status_interval_number = fields.Integer(string="Interval Number for Update Order Status")

    # Datetime fields
    inventory_export_next_execution = fields.Datetime(string='Next Execution for Export Stock ')
    import_order_next_execution = fields.Datetime(string='Next Execution for Import Order')
    order_status_next_execution = fields.Datetime(string='Next Execution for Update Order Status')

    # Selection fields
    inventory_export_interval_type = fields.Selection(
        selection=[('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
                   ('weeks', 'Weeks'), ('months', 'Months')],
        string='Interval Unit for Export Stock')
    import_order_interval_type = fields.Selection(
        selection=[('minutes', 'Minutes'), ('hours', 'Hours'),
                   ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
        string="Interval Unit for Import Order")
    order_status_interval_type = fields.Selection(
        selection=[('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'),
                   ('weeks', 'Weeks'), ('months', 'Months')],
        string="Interval Unit for Update Order Status")

    # Relational fields
    multi_ecommerce_connector_id = fields.Many2one(
        comodel_name="setu.multi.ecommerce.connector",
        string="Multi e-Commerce Connector", copy=False,
        default=_get_multi_ecommerce_connector, readonly=True)
    inventory_export_user_id = fields.Many2one(
        comodel_name="res.users", string="User for Export Inventory",
        default=lambda self: self.env.user)
    import_order_user_id = fields.Many2one(
        comodel_name="res.users", string="User for Import Order",
        default=lambda self: self.env.user)
    order_status_user_id = fields.Many2one(
        comodel_name="res.users", string="User for Update Order Status",
        default=lambda self: self.env.user)

    @api.constrains("inventory_export_interval_number", "import_order_interval_number", "order_status_interval_number")
    def check_interval_time(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use for check if interval time zero set is zero
        :return: None
        """
        for record in self:
            is_zero = False
            if record.stock_auto_export and record.inventory_export_interval_number <= 0:
                is_zero = True
            if record.order_auto_import and record.import_order_interval_number <= 0:
                is_zero = True
            if record.order_status_auto_update and record.order_status_interval_number <= 0:
                is_zero = True
            if is_zero:
                raise ValidationError(_("Cron Execution Time can't be set to as 0(Zero)."))

    def prepare_values_for_cron(self, interval_number, interval_type, user_id):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to prepare value for cron
        :param interval_number:
        :param interval_type:
        :param user_id:
        :return: dictionary
        """
        vals = {'active': True, 'interval_number': interval_number, 'interval_type': interval_type,
                'user_id': user_id.id if user_id else False}
        return vals

    def create_ir_module_data(self, module, name, new_cron):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to create record for ir.model.data
        :param module:
        :param name:
        :param new_cron:
        :return: ir model data record
        """
        self.env['ir.model.data'].create(
            {'module': module, 'name': name, 'model': 'ir.cron', 'res_id': new_cron.id, 'noupdate': True})

    def check_core_cron(self, name):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to create record for ir.model.data
        :param name:
        :return: cron
        """
        try:
            core_cron = self.env.ref(name)
        except:
            core_cron = False
        if not core_cron:
            raise ValidationError(
                _('Core settings of e-Commerce are deleted, Please upgrade the e-Commerce Base Module to back these settings.'))
        return core_cron

    def process_cron_configuration(self):
        """
        @name : Kamlesh Singh
        @date : 25/10/2024
        @purpose : This method will use to process cron configuration
        :return:
        """
        return {'type': 'ir.actions.client', 'tag': 'reload'}
