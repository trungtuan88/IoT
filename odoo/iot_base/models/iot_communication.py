from odoo import fields, models


class IoTCommunicationSystem(models.Model):
    _name = "iot.communication"
    _description = "IoT Communication System"

    name = fields.Char(required=True)
    device_ids = fields.One2many("iot.device", "iot_communication_id")
