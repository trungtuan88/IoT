from datetime import timedelta

from odoo import fields, models, api


class IoTPoints(models.Model):
    _name = 'iot.point'
    _description = 'IoT Points'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    iot_device_id = fields.Many2one('iot.device')
    iot_value_ids = fields.One2many('iot.value', 'iot_point_id')
    name = fields.Char(string="Name Point", help="Description of the point")
    point = fields.Char(string="Point", required=True, help="The unique identifier name of the point on the device.")
    token = fields.Char(related="iot_device_id.token", readonly=True)
    active = fields.Boolean(string="Active", default=True, help="Set it to False if you want to disable it, instead of deleting it.")
    type_signal = fields.Selection([
        ('input', 'Input'),
        ('output', 'Output'),
    ], string="Signal Type", default='input', required=True)
    type_data = fields.Selection([
        ('digital', 'Digital'),
        ('analog', 'Analog'),
        ('string', 'String'),
    ], string="Type Data", default='analog', required=True)
    last_value = fields.Char(string="Last Value", readonly=True)
    last_value_date = fields.Datetime(string="Last Value Date", readonly=True)
    is_monitored = fields.Boolean(string='Is Monitored', default=False)
    status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('not_monitored', 'Not Monitored')
    ], string='Status', default='not_monitored', compute="_compute_status", readonly=True)
    update_cycle = fields.Float(string='Update Cycle (s)', default=5, digits=(None, 1), help="Update cycle in seconds")


    _sql_constraints = [
        (
            "unique_point_uniq",
            "UNIQUE(point, iot_device_id)",
            "A device cannot have two duplicate points.",
        ),
    ]
    
    # @api.depends('iot_value_ids')
    # def _compute_last_value(self):
    #     for r in self:
    #         if r.iot_value_ids:
    #             r.last_value = str(r.iot_value_ids[-1].value)
    #             r.last_value_date = r.iot_value_ids[-1].create_date
    #         else:
    #             r.last_value = ""
    #             r.last_value_date = False

    @api.depends('last_value', 'last_value_date', 'is_monitored')
    def _compute_status(self):
        for r in self:
            if not r.is_monitored:
                r.status = 'not_monitored'
            else:
                # Kiểm tra thời gian của last_value_date
                # vì thời gian xử lý có thể bị chậm nên cần cộng thêm 0.5s
                if r.last_value_date and (fields.Datetime.now() - r.last_value_date) <= timedelta(seconds=(r.update_cycle + 0.5)):
                    r.status = 'connected'
                else:
                    r.status = 'disconnected'
