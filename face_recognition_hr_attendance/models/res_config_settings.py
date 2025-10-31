# -*- coding: utf-8 -*-

import base64
import io
import os
import pickle

import cv2
import face_recognition
import numpy as np

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    file_path = fields.Char(string="Encoding File Path")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'face_recognition_hr_attendance.file_path', self.file_path)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        file_path = ICPSudo.get_param('face_recognition_hr_attendance.file_path')
        res.update(file_path=file_path)
        return res

    def action_generate_face_encodings(self):
        """
        Llama al método centralizado de generación de encodings desde hr.employee.
        """
        self.env['hr.employee'].save_encodings()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Face encodings have been saved to disk.'),
                'sticky': False,
            }
        }
