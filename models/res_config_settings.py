
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    cancle_days = fields.Integer(string='Cancel Days', config_parameter='om_hospital.cancle_days')
