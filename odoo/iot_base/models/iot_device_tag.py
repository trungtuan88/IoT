from odoo import fields, models


class IotDeviceTag(models.Model):
    _name = "iot.device.tag"
    _description = "Device Tag"


    def _get_default_color(self):
        return randint(1, 20)

    name = fields.Char(required=True)
    color = fields.Integer(string="Color Index", default=_get_default_color)
