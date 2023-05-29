from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class OdooPlayGround(models.Model):
    _name = "odoo.playground"
    _description = "Odoo Playground"

    DEFAULT_ENV_VARIABLES = """# Available variable:
    # - self: Current object
    # - self.env: Odoo Environment on which the action is triggered
    # - self.env.user : Return the current user (as an instance)
    # - self.env.is_system: Return whether the current user has group "Setting", or is  in superuser mode.
    # - self.env.is_admin: Return whether the current user has group "Access Right", or is  in superuser mode.
    # - self.env.is_superuser: Return whether the environment is  in superuser mode.
    # - self.env.company: Return the current company (as an instance)
    # - self.env.companies: Return a recordset of the enable companies by the user
    # - self.env.lang: Return the current language code \n\n\n\n """

    model_id = fields.Many2one('ir.model', string='Model')
    code = fields.Text(string='Code', default = DEFAULT_ENV_VARIABLES)
    result = fields.Text(string='Result')

    # field_get = self.env['hospital.patient'].fields_get(['name','gender'],['type','string'])
    # get_metadeta = self.env['patient.tag'].browse(99).get_metadata()
    # search_count = self.env['hospital.patient'].search_count(['|',('gender','=','male'),('gender','=','female')], count=True)
    # search = self.env['hospital.patient'].search([('gender','=','female'),('id','=',6)])
    # search = self.env['hospital.patient'].search([], limit=50, order='id desc, name')
    # browse = self.env['hospital.patient'].browse(72).exist()
    # browse = self.env['hospital.patient'].browse(72)
    # browse.copy() -- copy method
    # browse.unlink() -- unlink method
    # unlink = self.env['hospital.patient'].browse(72.'id').unlink()
    # write = self.env['hospital.patient'].browse(72).write('name':'om','email':'dummay@gmail.com')
    # create = self.env['hospital.patient'].create({'name':'om','email':'dummay@gmail.com'})
    # ref = self.env.ref('om_hospital.patient_xyz')
    # print("Alexander", ref)
    # partners = self.env['res.parents'].search([])
    # print("partner..", partner.mapped('email')) -- mapped operation


    def action_execute(self):
        try:
            if self.model_id:
                model = self.env[self.model_id.model]
            else:
                model = self
            self.result = safe_eval(self.code.strip(), {'self' : model})
        except Exception as e:
            self.result = str(e)