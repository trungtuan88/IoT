import uuid
import threading
import json
import re

from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import AccessDenied


class IoTInput(http.Controller):

    @http.route('/iot/device/<string:token>/info', type='http', auth='none', methods=['GET'], csrf=False)
    def iot_info(self, token=None, ip=None, mac=None, version=None, last_update=None, **kw):
        iot_device = request.env['iot.device'].sudo().search([('token', '=', token)], limit=1)
        if not iot_device:
            return Response(status=404)
        iot_device.write({
            'ip': ip,
            'mac': mac,
            'version': version,
            'last_update': last_update,
        })
        return Response(status=200)

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
        res = dict()
        for point_tag, point_value in params.items():
            value, type_data = self._determine_type_data(point_value)
            iot_point = iot_device.iot_point_ids.filtered(
                lambda p: p.point == point_tag and p.type_signal == 'input' and p.type_data == type_data)
            if not iot_point:
                res[point_tag] = 'not_found'
                continue
            if iot_point.last_value == value:
                iot_point.last_value_date = fields.Datetime.now()
                continue
            iot_value = request.env['iot.value'].sudo().create({
                'iot_point_id': iot_point.id,
                'value_boolean': value if type_data == 'digital' else None,
                'value_analog': value if type_data == 'analog' else None,
                'value_char': value if type_data == 'string' else None,
            })
            res[point_tag] = 'updated'
        return res

    def _determine_type_data(self, value):
        if isinstance(value, str) and value.lower() in ['true', 'false', 'on', 'off']:
            value = value.lower() == 'true' or value.lower() == 'on'
            type_data = 'digital'
        elif isinstance(value, (int, float)):
            value = float(value)
            type_data = 'analog'
        else:
            type_data = 'string'
        return value, type_data
