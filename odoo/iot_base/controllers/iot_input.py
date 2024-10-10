import uuid
import threading
import json
import re

from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import AccessDenied


class IoTInput(http.Controller):

    @http.route('/iot/device/<string:token>/input', type='json', auth='none', methods=['POST'], csrf=False)
    def iot_input(self, token=None, **kw):
        iot_device = request.env['iot.device'].sudo().search([('token', '=', token)], limit=1)
        if not iot_device:
            return Response(status=404)
        """
            {
                "point_tag_1": "value_1",
                "point_tag_2": "value_2",
                "point_tag_3": "value_3",
            }
        """
        params = request.get_json_data()
        for point, value in params.items():
            if isinstance(value, str) and value.lower() in ['true', 'false', 'on', 'off']:
                value = value.lower() == 'true' or value.lower() == 'on'
            iot_point = iot_device.iot_point_ids.filtered(lambda p: p.point == point and p.type_signal == 'input')
            if not iot_point:
                iot_point = request.env['iot.point'].sudo().create({
                    'iot_device_id': iot_device.id,
                    'point': point,
                    'type_signal': 'input',
                    'type_data': 'analog' if isinstance(value, (int, float)) else 'digital' if isinstance(value, bool) else 'string' if isinstance(value, str) else None,
                })
            if iot_point.last_value == value:
                iot_point.last_value_date = fields.Datetime.now()
                continue
            iot_value = request.env['iot.value'].sudo().create({
                'iot_point_id': iot_point.id,
                'value_boolean': value if isinstance(value, bool) else None,
                'value_analog': float(value) if isinstance(value, (int, float)) else None,
                'value_char': value if isinstance(value, str) else None,
            })
        return None
