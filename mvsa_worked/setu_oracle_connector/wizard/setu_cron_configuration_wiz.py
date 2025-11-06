from odoo import api, fields, models
from datetime import datetime
from odoo.addons.setu_ecommerce_based.wizard.setu_cron_configuration_wiz import _intervalTypes


class SetuCronConfigurationWiz(models.TransientModel):
    _inherit = 'setu.cron.configuration.wiz'

    # def process_cron_configuration(self):
    #     if self.multi_ecommerce_connector_id.ecommerce_connector == 'oracle_connector':
    #         ecommerce_connector_id = self.multi_ecommerce_connector_id
    #         self.setup_oracle_inventory_export_cron(ecommerce_connector_id)
    #         self.setup_oracle_import_order_cron(ecommerce_connector_id)
    #     return super(SetuCronConfigurationWiz, self).process_cron_configuration()
    #
    # def setup_oracle_inventory_export_cron(self, ecommerce_connector_id):
    #     try:
    #         cron_exist = self.env.ref(
    #             'setu_oracle_connector.ir_cron_auto_export_product_inventory_ecommerce_connector_%d' % ecommerce_connector_id.id)
    #     except:
    #         cron_exist = False
    #     if self.stock_auto_export:
    #         nextcall = datetime.now() + _intervalTypes[self.inventory_export_interval_type](
    #             self.inventory_export_interval_number)
    #         vals = self.prepare_values_for_cron(self.inventory_export_interval_number,
    #                                             self.inventory_export_interval_type, self.inventory_export_user_id)
    #         vals.update({'nextcall': self.inventory_export_next_execution or nextcall.strftime('%Y-%m-%d ''%H:%M:%S'),
    #                      'code': "model.cron_auto_update_stock_in_oracle(ctx={'multi_ecommerce_connector_id':%d})" % ecommerce_connector_id.id})
    #         if cron_exist:
    #             vals.update({'name': cron_exist.name})
    #             cron_exist.write(vals)
    #         else:
    #             core_cron = self.check_core_cron("setu_oracle_connector.ir_cron_process_oracle_export_stock")
    #             name = ecommerce_connector_id.name + " : " + dict(
    #                 ecommerce_connector_id._fields['ecommerce_connector'].selection).get(
    #                 ecommerce_connector_id.ecommerce_connector) + ' : ' + core_cron.name
    #             vals.update({'name': name})
    #             new_cron = core_cron.copy(default=vals)
    #             name = 'ir_cron_auto_export_product_inventory_ecommerce_connector_%d' % (ecommerce_connector_id.id)
    #             module = 'setu_oracle_connector'
    #             self.create_ir_module_data(module, name, new_cron)
    #     else:
    #         if cron_exist:
    #             cron_exist.write({'active': False})
    #     return True
    #
    # def setup_oracle_import_order_cron(self, ecommerce_connector_id):
    #     try:
    #         cron_exist = self.env.ref(
    #             'setu_oracle_connector.ir_cron_oracle_auto_import_order_ecommerce_connector_%d' % ecommerce_connector_id.id)
    #     except:
    #         cron_exist = False
    #     if self.order_auto_import:
    #         nextcall = datetime.now() + _intervalTypes[self.import_order_interval_type](
    #             self.import_order_interval_number)
    #         vals = self.prepare_values_for_cron(self.import_order_interval_number, self.import_order_interval_type,
    #                                             self.import_order_user_id)
    #         vals.update({'nextcall': self.import_order_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
    #                      'code': "model.cron_auto_import_oracle_order(ctx={'multi_ecommerce_connector_id':%d})" % ecommerce_connector_id.id})
    #         if cron_exist:
    #             vals.update({'name': cron_exist.name})
    #             cron_exist.write(vals)
    #         else:
    #             core_cron = self.check_core_cron("setu_oracle_connector.ir_cron_process_oracle_import_orders")
    #             name = ecommerce_connector_id.name + " : " + dict(
    #                 ecommerce_connector_id._fields['ecommerce_connector'].selection).get(
    #                 ecommerce_connector_id.ecommerce_connector) + ' : ' + core_cron.name
    #             vals.update({'name': name})
    #             new_cron = core_cron.copy(default=vals)
    #             name = 'ir_cron_oracle_auto_import_order_ecommerce_connector_%d' % (ecommerce_connector_id.id)
    #             module = 'setu_oracle_connector'
    #             self.create_ir_module_data(module, name, new_cron)
    #     else:
    #         if cron_exist:
    #             cron_exist.write({'active': False})
    #     return True
