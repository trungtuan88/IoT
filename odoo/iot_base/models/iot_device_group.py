from odoo import fields, models


class IotDeviceGroup(models.Model):
    _name = "iot.device.group"
    _description = "Iot Group"

    name = fields.Char(required=True)
