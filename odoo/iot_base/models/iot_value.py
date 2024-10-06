from odoo import fields, models


class IoTPoints(models.Model):
    _name = 'iot.value'
    _description = 'IoT Value'


    iot_point_id = fields.Many2one('iot.point')
    value_boolean = fields.Boolean(string="Value Boolean")
    value_analog = fields.Float(string="Value Analog", digits="IoT Value Analog")
    value_char = fields.Char(string="Value Char")