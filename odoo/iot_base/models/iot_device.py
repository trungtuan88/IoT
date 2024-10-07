import secrets

from odoo import fields, models, api


class IoTDevice(models.Model):
    _name = "iot.device"
    _description = "IoT Device"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _check_company_auto = True

    name = fields.Char(string="Name Device", required=True)
    iot_communication_id = fields.Many2one("iot.communication", required=True)
    active = fields.Boolean(string="Active", default=True, help="Set it to False if you want to disable it, instead of deleting it.")
    # state = fields.Selection(
    #     [],
    #     readonly=True
    #     )
    ip = fields.Char(string="IP", readonly=True, help="IP address of the device")
    group_id = fields.Many2one("iot.device.group", help="Group the devices together")
    tag_ids = fields.Many2many("iot.device.tag")
    last_update = fields.Datetime(string="Last Update", readonly=True, help="Last version update time")
    version = fields.Char(string="Version", readonly=True, help="Firmware version")
    model = fields.Char(string="Model", help="Device model")
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Favorite'),
    ], default='0', string="Favorite")
    iot_point_ids = fields.One2many('iot.point', 'iot_device_id')
    count_point_input = fields.Integer(string="Point Input", compute="_compute_count_point", help="Number of input points")
    count_point_output = fields.Integer(string="Point Output", compute="_compute_count_point", help="Number of output points")
    token = fields.Char(string="Token", readonly=True, help="This code is used to authenticate the device with the system.\
        The system also uses this code to manage the points assigned to that device.")

    @api.depends('iot_point_ids')
    def _compute_count_point(self):
        count_input = self.env['iot.point']._read_group([('iot_device_id', 'in', self.ids), ('signal_type', '=', 'input')], ['iot_device_id'], ['__count'])
        count_output = self.env['iot.point']._read_group([('iot_device_id', 'in', self.ids), ('signal_type', '=', 'output')], ['iot_device_id'], ['__count'])
        mapped_data_input = {point_input.id: count for point_input, count in count_input}
        mapped_data_output = {point_output.id: count for point_output, count in count_output}
        for r in self:
            r.count_point_input = mapped_data_input.get(r.id, 0)
            r.count_point_output = mapped_data_output.get(r.id, 0)
    
    def action_open_point_input(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('iot_base.iot_point_action')
        
        action['context'] = {
            'default_iot_device_id': self.id,
            'default_signal_type': 'input',
        }
        if self.count_point_input == 0:
            action['view_mode'] = 'form'
            # action['res_id'] = self.iot_point_ids.id
            # action['views'] = []
        else:
            action['view_mode'] = 'tree'
            action['domain'] = [('iot_device_id', '=', self.id), ('signal_type', '=', 'input')]
        return action
    
    def action_open_point_output(self):
        action = self.env['ir.actions.act_window']._for_xml_id('iot_base.iot_point_action')
        action['domain'] = [('iot_device_id', 'in', self.ids), ('signal_type', '=', 'output')]
        return action
    
    def action_generate_token(self):
        self.ensure_one()
        alphabet = 'abcdefghijkmnpqrstuvwxyz0123456789'
        while True:
            token = '-'.join(''.join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))
            if not self.env['iot.device'].search([('token', '=', token)]):
                break
        self.token = token.upper()
        return True
