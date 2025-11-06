# -*- coding: utf-8 -*-
import base64
import io
import os
import pickle
import json

import cv2
import face_recognition
import numpy as np

from odoo import models, fields, api, _, http
from odoo.exceptions import ValidationError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class EmpImages(models.Model):
    _name = "hr.employee.image"
    _description = "Employee Face Recognition Image"

    name = fields.Char(required=True)
    image_data = fields.Image(required=True)
    hr_employee_id = fields.Many2one("hr.employee", string="Employee", ondelete='cascade')

    @api.onchange("image_data")
    def validate_img(self):
        if self.image_data:
            cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
            haar_model = os.path.join(cv2_base_dir, 'data/haarcascade_frontalface_default.xml')
            face_cascade = cv2.CascadeClassifier(haar_model)

            image_stream = io.BytesIO(base64.b64decode(self.image_data))
            image_stream.seek(0)
            file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is None:
                raise ValidationError("❌ The uploaded image could not be decoded. Please use another image format.")

            max_dim = 1600
            height, width = img.shape[:2]
            if max(height, width) > max_dim:
                scale = max_dim / max(height, width)
                new_size = (int(width * scale), int(height * scale))
                img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)

            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_img, 1.1, 4)

            if len(faces) < 1:
                raise ValidationError("❌ No face detected. Please upload a clear image showing your face.")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    recognition_image_ids = fields.One2many(
        'hr.employee.image', 'hr_employee_id', string="Face recognition employee's images", copy=True)

    def _get_company_pickle_path(self):
        """Devuelve (company_dir, file_path) para la compañía actual."""
        ICPSudo = self.env['ir.config_parameter'].sudo()
        base_path = ICPSudo.get_param('face_recognition_hr_attendance.file_path')
        if not base_path:
            raise ValidationError("System parameter 'face_recognition_hr_attendance.file_path' is not configured.")
        company = self.env.company
        company_dir = os.path.join(base_path, f"company_{company.id}")
        os.makedirs(company_dir, exist_ok=True)  # crea la carpeta si no existe
        file_path = os.path.join(company_dir, "encodings.pickle")
        return company_dir, file_path

    def save_encodings(self):
        # Ruta por compañía
        _, file_path = self._get_company_pickle_path()

        known_encodings = []
        known_names = []

        employee_ids = self.env["hr.employee"].sudo().search([
            ("recognition_image_ids", "!=", False),
            ("barcode", "!=", False)
        ])

        if not employee_ids:
            _logger.warning("No hay empleados con imágenes y códigos de barras para generar codificaciones.")
            with open(file_path, "wb") as f:
                pickle.dump({"encodings": [], "names": []}, f)
            _logger.info("📦 Encodings vacías guardadas en %s (no había empleados válidos).", file_path)
            return

        for emp_id in employee_ids:
            for emp_img_id in emp_id.recognition_image_ids:
                try:
                    image_stream = io.BytesIO(base64.b64decode(emp_img_id.image_data))
                    face_image = face_recognition.load_image_file(image_stream)
                    face_encodings = face_recognition.face_encodings(face_image)

                    if not face_encodings:
                        _logger.warning("🚫 No se detectó un rostro en la imagen del empleado %s (%s).", emp_id.name, emp_id.id)
                        continue

                    known_encodings.append(face_encodings[0])
                    # guardamos el BARCODE (lo espera el controlador para buscar empleado)
                    known_names.append(emp_id.barcode)
                    _logger.info("✅ Codificación guardada para %s (Barcode: %s).", emp_id.name, emp_id.barcode)

                except Exception as e:
                    _logger.error("❌ Error al procesar la imagen del empleado %s: %s", emp_id.name, e)

        if not known_encodings:
            _logger.warning("⚠️ No se encontraron codificaciones válidas. No se creará/actualizará el archivo.")
            return

        try:
            with open(file_path, "wb") as f:
                pickle.dump({"encodings": known_encodings, "names": known_names}, f)
            _logger.info("📦 Encodings guardadas en %s. Total: %d", file_path, len(known_encodings))
        except Exception as e:
            _logger.error("❌ Fallo al guardar las codificaciones: %s", e)
            raise

    @api.model
    def attendance_scan(self, barcode, img=None):
        _logger.info("Registro de asistencia para el código de barras: %s", barcode)
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            _logger.info("Empleado encontrado con barcode %s: ID -> %d, Nombre -> %s", barcode, employee.id, employee.name)
            result = employee._attendance_action('hr_attendance.hr_attendance_action_kiosk_mode')
            action = result.get("action")
            if img and not isinstance(img, dict):
                img_str = img.split(",", 1)
                if len(img_str) == 2:
                    img_base64 = img_str[1].encode()
                    attendance = action.get("attendance")
                    if attendance:
                        attendance_id = self.env["hr.attendance"].browse(attendance.get("id"))
                        attendance_id.attendance_by = "facial_recognition"
                        if not attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_in_image = img_base64
                        elif attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_out_image = img_base64
            _logger.info("Asistencia registrada con éxito para: %s", employee.name)
            return result
        _logger.warning("No se encontró ningún empleado con el código de barras: %s", barcode)
        return {'warning': _('No employee corresponding to barcode %(barcode)s') % {'barcode': barcode}}


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_by = fields.Selection([
        ("other", "Other"),
        ("facial_recognition", "Facial Recognition"),
    ], default="other", string="Attendance Mode")
    check_in_image = fields.Image()
    check_out_image = fields.Image()


class ResCompany(models.Model):
    _inherit = "res.company"

    attendance_kiosk_mode = fields.Selection(selection_add=[
        ("facial_recognition", "Facial Recognition")
    ], ondelete={'facial_recognition': 'set default'})


class FaceRecognitionController(http.Controller):

    @http.route('/emp/attendance/img', type='http', auth="public", website=True, csrf=False, cors="*")
    def recognize_face_and_get_employee_data(self, **kw):
        _logger.info("📸 Recibiendo imagen para reconocimiento facial...")

        ICPSudo = request.env['ir.config_parameter'].sudo()
        base_path = ICPSudo.get_param('face_recognition_hr_attendance.file_path')
        if not base_path:
            _logger.error("La ruta de codificaciones faciales no está configurada.")
            return json.dumps({'error': 'La ruta de codificaciones faciales no está configurada.'})

        # Ruta por compañía
        company = request.env.company
        company_dir = os.path.join(base_path, f"company_{company.id}")
        file_path = os.path.join(company_dir, "encodings.pickle")

        # Fallback: archivo plano legacy si aún no existe por compañía
        if not os.path.exists(file_path):
            legacy = os.path.join(base_path, "encodings.pickle")
            if os.path.exists(legacy):
                _logger.warning("Usando encodings legacy en %s (no se encontró por compañía).", legacy)
                file_path = legacy
            else:
                _logger.error("Encodings file not found for company %s at: %s", company.name, file_path)
                return json.dumps({'error': f'Encodings file not found for company {company.name} at : {file_path}'})

        try:
            with open(file_path, "rb") as file:
                data = pickle.load(file)
                known_face_encodings = data.get('encodings', [])
                known_face_barcodes = data.get('names', [])
        except Exception as e:
            _logger.error("Error al cargar el archivo de codificaciones (%s): %s", file_path, e)
            return json.dumps({'error': 'Error interno del servidor al cargar las codificaciones.'})

        # Imagen recibida desde el frontend
        try:
            img_b64 = kw.get('img', '')
            img_data_b64 = img_b64.split(',', 1)[1] if ',' in img_b64 else img_b64
            img_data = base64.b64decode(img_data_b64)
            img_buffer = io.BytesIO(img_data)
            face_image = face_recognition.load_image_file(img_buffer)
            unknown_face_encodings = face_recognition.face_encodings(face_image)
        except Exception as e:
            _logger.error("Error al procesar la imagen de la cámara: %s", e)
            return json.dumps({'error': 'Error al procesar la imagen de la cámara.'})

        if not unknown_face_encodings:
            return json.dumps({'error': 'No se detectó un rostro en la imagen.'})

        if not known_face_encodings:
            return json.dumps({'error': 'No hay modelo de reconocimiento disponible. Genere el modelo primero.'})

        distances = face_recognition.face_distance(known_face_encodings, unknown_face_encodings[0])
        match_index = int(np.argmin(distances))

        match_threshold = 0.7
        ambiguity_threshold = 0.05

        if distances[match_index] < match_threshold:
            sorted_distances = np.sort(distances)
            best_match_distance = float(sorted_distances[0])

            if len(sorted_distances) > 1:
                second_best_match_distance = float(sorted_distances[1])
                if (second_best_match_distance - best_match_distance) < ambiguity_threshold:
                    _logger.warning("Coincidencia ambigua: best=%s second=%s", best_match_distance, second_best_match_distance)

            employee_barcode = known_face_barcodes[match_index]
            employee = request.env['hr.employee'].sudo().search([('barcode', '=', employee_barcode)], limit=1)

            if employee and employee.barcode:
                _logger.info("Rostro reconocido como %s (Barcode: %s).", employee.name, employee_barcode)
                return json.dumps({
                    'employee_id': employee.id,
                    'name': employee.name,
                    'barcode': employee.barcode,
                    'status': 'success'
                })

            _logger.warning("Rostro reconocido, pero el empleado no tiene código de barras (%s).", employee_barcode)
            return json.dumps({'error': 'Rostro reconocido, pero el empleado no tiene un código de barras. Por favor, contacte a un administrador.'})

        _logger.info("Rostro no reconocido. Distancia mínima: %s", float(distances[match_index]))
        return json.dumps({'error': 'Rostro no reconocido. Por favor, inténtelo de nuevo.'})