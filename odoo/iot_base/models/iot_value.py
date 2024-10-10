from odoo import fields, models, api


class IoTPoints(models.Model):
    _name = 'iot.value'
    _description = 'IoT Value'

    iot_point_id = fields.Many2one('iot.point')
    value_boolean = fields.Boolean(string="Value Boolean", readonly=True, inverse='_set_last_value')
    value_analog = fields.Float(string="Value Analog", digits="IoT Value Analog",
                               readonly=True, inverse='_set_last_value')
    value_char = fields.Char(string="Value Char", readonly=True, inverse='_set_last_value')

    def _set_last_value(self):
        for r in self:
            if r.iot_point_id.type_data == 'digital':
                r.iot_point_id.last_value = "False" if not r.value_boolean else "True"
            elif r.iot_point_id.type_data == 'analog':
                r.iot_point_id.last_value = r.value_analog
            else:
                r.iot_point_id.last_value = r.value_char
            r.iot_point_id.last_value_date = r.create_date
