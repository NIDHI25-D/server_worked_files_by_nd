# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class SetuProcessHistoryLine(models.Model):
    _inherit = "setu.process.history.line"

    def mirakl_prepare_process_history_line_vals(self, message, model_id, process_history_id,record_id):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 05/05/25
            Task: Migration to v18 from v16
            Purpose: creates a record of process history line for mirakl order.
        """
        vals = self.create({'message': message,
                'order_ref':record_id,
                'model_id': model_id,
                'process_history_id': process_history_id.id if process_history_id else False})
        return vals
