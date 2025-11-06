# -*- coding: utf-8 -*-
import base64
import io
import json
import pickle
import os

import cv2
import face_recognition
import numpy as np

from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


# ---------- Helpers compartidos ----------
def _get_company_by_token(token):
    """Busca la compañía asociada al token de kiosco."""
    return request.env['res.company'].sudo().search([('attendance_kiosk_key', '=', token)], limit=1)


def _resolve_pickle_path(base_path, company_id):
    """
    Devuelve la ruta del pickle:
    1) company_<id>/encodings.pickle (si existe)
    2) legacy encodings.pickle en la raíz (si existe)
    Si no existe ninguno, devuelve None.
    """
    company_dir = os.path.join(base_path, f"company_{company_id}")
    company_pickle = os.path.join(company_dir, "encodings.pickle")
    if os.path.exists(company_pickle):
        return company_pickle

    legacy_pickle = os.path.join(base_path, "encodings.pickle")
    if os.path.exists(legacy_pickle):
        _logger.warning("Usando pickle legacy en %s (no encontrado por compañía).", legacy_pickle)
        return legacy_pickle

    return None


def _decode_b64_to_cv_image(img_b64_bytes):
    """
    Recibe bytes base64 (sin encabezado data:) y devuelve imagen BGR (cv2).
    """
    image_stream = io.BytesIO(base64.b64decode(img_b64_bytes))
    image_stream.seek(0)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)  # BGR
    return img


class FaceRecognitionHrAttendance(http.Controller):
    """
    Controlador para gestionar la lógica de reconocimiento facial en Odoo.
    """

    @http.route('/emp/attendance/img', type='http', auth="public", methods=['POST'], csrf=False)
    def index(self, **kw):
        """
        Endpoint HTTP para recibir una imagen codificada en base64 y procesarla.
        Respuesta JSON: {"name": "...", "barcode": "..."} o {"error": "..."}.
        """
        img = kw.get("img")
        token = kw.get("token")
        if not img or not token:
            return json.dumps({"error": "Missing image or token."})

        names = []
        img_str = img.split(",", 1)
        if len(img_str) == 2:
            img_base64_bytes = img_str[1].encode()
            names = self.classify_face(img_base64_bytes, token)

        if not names:
            return json.dumps({"error": "No match found! Scan your face again or contact admin."})

        if len(names) > 1:
            return json.dumps({"error": "Multiple match found! Scan your face again."})

        label = names[0]
        if label == "Unknown":
            return json.dumps({"error": "No match found! Scan your face again or contact admin."})

        # Compatibilidad: si el pickle trae IDs numéricos (legacy) o barcodes (actual)
        emp = None
        if str(label).isdigit():
            emp = request.env["hr.employee"].sudo().browse(int(label))
            if not emp or not emp.exists():
                emp = None
        if emp is None:
            emp = request.env["hr.employee"].sudo().search([('barcode', '=', str(label))], limit=1)

        if emp:
            return json.dumps({"name": emp.name, "barcode": emp.barcode})
        else:
            return json.dumps({"error": "No match found! Scan your face again or contact admin."})

    def classify_face(self, unknown_img_b64_bytes, token):
        """
        Clasifica una imagen desconocida comparándola con encodings faciales existentes.
        Soporta múltiples empresas utilizando el token de kiosco y tiene fallback a pickle legacy.
        Retorna una lista de labels (IDs o barcodes) o ["Unknown"].
        """
        ICPSudo = request.env['ir.config_parameter'].sudo()
        base_path = ICPSudo.get_param('face_recognition_hr_attendance.file_path')
        if not base_path:
            _logger.error("Encoding File Path not set in system parameters!")
            return []

        company = _get_company_by_token(token)
        if not company:
            _logger.error("Invalid token: company not found.")
            return []

        encodings_file_path = _resolve_pickle_path(base_path, company.id)
        if not encodings_file_path:
            _logger.error("Encodings file not found for company %s under %s", company.name, base_path)
            return []

        try:
            with open(encodings_file_path, "rb") as f:
                data = pickle.load(f)
                known_encodings = data.get("encodings", [])
                known_names = data.get("names", [])
        except Exception as e:
            _logger.error("Error loading face encodings file %s: %s", encodings_file_path, e)
            return []

        if not known_encodings:
            _logger.warning("No encodings in %s.", encodings_file_path)
            return []

        # Decodificar la imagen recibida
        try:
            img_bgr = _decode_b64_to_cv_image(unknown_img_b64_bytes)
            if img_bgr is None:
                _logger.error("Unknown image could not be decoded.")
                return []
            # CV2 es BGR, la lib de face_recognition usa RGB
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        except Exception as e:
            _logger.error("Error decoding unknown image: %s", e)
            return []

        # Localización + encodings
        face_locations = face_recognition.face_locations(img_rgb, model="hog")
        unknown_face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

        face_names = []
        if not unknown_face_encodings:
            _logger.info("No face encoding detected in image.")
            return face_names

        # Umbrales
        tolerance = 0.5              # más estricto que 0.6
        ambiguity_gap = 0.05         # diferencia mínima entre 1º y 2º distancia

        for face_encoding in unknown_face_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if distances.size == 0:
                face_names.append("Unknown")
                continue

            order = np.argsort(distances)
            best_idx = int(order[0])
            best_d = float(distances[best_idx])
            second_d = float(distances[order[1]]) if len(order) > 1 else 1.0

            _logger.info("Distances -> best=%.4f second=%.4f (tol=%.2f)", best_d, second_d, tolerance)

            if best_d < tolerance:
                if (second_d - best_d) < ambiguity_gap:
                    _logger.warning("Ambiguous match: best=%.4f second=%.4f (gap=%.4f)", best_d, second_d, second_d - best_d)
                    face_names.append("Unknown")
                else:
                    label = known_names[best_idx]
                    _logger.info("Match found: %s (distance=%.4f)", label, best_d)
                    face_names.append(str(label))
            else:
                _logger.info("Face not recognized. Closest distance: %.4f", best_d)
                face_names.append("Unknown")

        return face_names


class HrAttendanceFacial(HrAttendance):
    @http.route('/hr_attendance/attendance_barcode_scanned', type="json", auth="public")
    def scan_barcode(self, token, barcode, img=None):
        company = _get_company_by_token(token)
        if company:
            employee = request.env['hr.employee'].sudo().search(
                [('barcode', '=', barcode), ('company_id', '=', company.id)],
                limit=1
            )
            if employee:
                attendance_id = employee._attendance_action_change(self._get_geoip_response('kiosk'))
                if img and not isinstance(img, dict) and attendance_id:
                    img_str = img.split(",", 1)
                    if len(img_str) == 2:
                        img_base64 = img_str[1].encode()
                        attendance_id.attendance_by = "facial_recognition"
                        if not attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_in_image = img_base64
                        elif attendance_id.check_in_image and not attendance_id.check_out_image:
                            attendance_id.check_out_image = img_base64
                return self._get_employee_info_response(employee)
        return {}