from odoo import api, fields, models


# access.hospital.operation,access_hospital_operation,om_hospital.model_hospital_operation,base.group_user,1,1,1,1

class HospitalOperation(models.model):
    _name = "hospital.operation"
    _description = "Hospital Operation"
    _log_access = False
    _order = "sequence" 

    doctor_id = fields.Many2one('res.users', string='Doctor')
    operation_name = fields._String('Name')
    reference_reccord = fields.Reference(selection=[('hospital.patient','Patient'),
                                                    ('hospital.appointment', 'Appointment')], string="Record")
    sequence = fields.Integer(string="sequence")

    @api.model
    def name_create(self,name):
        return self.name_create({'operation_name': name}).name_get()[0]




    # class ResGroups(models.Model):
    #     _inherit = 'res.group'


    #     def get_application_group(self, domain):
    #         group_id = self.env.ref('project.group_project_task_dependencies').id
    #         wave_group_id = self.env.ref('stock.group_stock_picking"_wave').id
    #         return super(ResGroups, self).get_application_group(domain+[('id', 'not in', (group_id, wave_group_id))])