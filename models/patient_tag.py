from odoo import api, models, fields, _

class HospitalPatient(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True, copy=False)
    color = fields.Integer(string='Color')
    color_2 = fields.Char(string='Color 2')

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
         if default is None:
              default = {}
   
         if not default.get('name'):
                default['name'] = self.name + "(copy)"
         return super(HospitalPatient, self).copy(default)

    _sql_constrains = [
        ('tagname_unique', 'unique(name)', 'This name is already used!')
    ]