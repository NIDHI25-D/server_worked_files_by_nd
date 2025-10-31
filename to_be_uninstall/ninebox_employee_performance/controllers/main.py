from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

import json
from odoo.tools import html2plaintext, html_escape


class NineboxReport(http.Controller):

    @http.route('/ninebox_report/pdf/', type='http', auth='user')
    def ninebox_report(self, data, token, **kw):
        requestcontent = json.loads(data)
        period = requestcontent[0]
        if not period:
            raise ValidationError("")
        try:
            pdf = request.env.ref('ninebox_employee_performance.action_report_ninebox').sudo().with_context(
                period=period)._render_qweb_pdf('ninebox_employee_performance.report_ninebox', period)[0]
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', 'attachment; filename=' + period + '.pdf;')

            ]
            response = request.make_response(pdf, headers=pdfhttpheaders)
            response.set_cookie('fileToken', token)
            return response

        except Exception as e:
            se = http.serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
