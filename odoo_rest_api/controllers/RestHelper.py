from odoo import _
from odoo.http import Response
from typing import Optional, Dict
from importlib.metadata import version


class RestHelper:

    @staticmethod
    def JsonValidResponse(data: any, valid_code: Optional[int] = 200) -> Dict[str, any]:
        """
        Return a JsonResponse with the given data and status code if code is valid or no exceptions.
        """
        if version("werkzeug") == '2.0.2':
            Response.status_code = valid_code
        if version("werkzeug") == '0.16.1':
            Response.status = str(valid_code)
        return {
            'status_code': valid_code,
            'message': _('success'),
            'data': data,
            'success': True
        }

    @staticmethod
    def JsonErrorResponse(error: any, error_code: Optional[int] = 400) -> Dict[str, any]:
        """
        Return a JsonResponse with the given data and status code if code is not valid or with exceptions.
        """
        if version("werkzeug") == '2.0.2':
            Response.status_code = error_code
        if version("werkzeug") == '0.16.1':
            Response.status = str(error_code)
        return {
            'code': error_code,
            'message': _('failed'),
            'error': error,
            'success': False
        }
