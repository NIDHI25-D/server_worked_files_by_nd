# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SetuProcessHistory(models.Model):
    _inherit = "setu.process.history"

    # def create_oracle_process_history(self, history_perform, multi_ecommerce_connector_id, model_id):
    #     process_history_id = self.create({"history_perform": history_perform,
    #                                       "ecommerce_connector": "oracle_connector",
    #                                       "multi_ecommerce_connector_id": multi_ecommerce_connector_id.id if multi_ecommerce_connector_id else False,
    #                                       "model_id": model_id,
    #                                       "active": True})
    #     return process_history_id
