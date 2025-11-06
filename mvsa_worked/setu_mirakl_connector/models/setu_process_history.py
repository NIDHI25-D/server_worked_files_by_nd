# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SetuProcessHistory(models.Model):
    _inherit = "setu.process.history"

    def create_mirakl_process_history(self, history_perform, multi_ecommerce_connector_id, model_id):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: creates a record of process history for mirakl order.
        """
        process_history_id = self.create({"history_perform": history_perform,
                                          "ecommerce_connector": "mirakl_connector",
                                          "multi_ecommerce_connector_id": multi_ecommerce_connector_id.id if multi_ecommerce_connector_id else False,
                                          "model_id": model_id,
                                          "active": True})
        return process_history_id
