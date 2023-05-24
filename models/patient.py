from datetime import date
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Hospital Patient"
    _rec_name="name"

    name = fields.Char(string="Name", tracking=True)
    date_of_birth = fields.Date(string='Date of Birth')
    ref = fields.Char(string="Reference")
    age = fields.Integer(string="Age", compute='_compute_age', inverse='_inverse_compute_age', search="_search_age", tracking=True)
    gender = fields.Selection([('male', 'Male'),('female', 'Female')],string="Gender", tracking=True, default='male')
    active = fields.Boolean(string="Active", default=True)
    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    image = fields.Image(string="Image")
    tag_ids = fields.Many2many('patient.tag', string="Tags")
    appointment_count = fields.Integer(string="Appointment Count", compute='_compute_appointment_count', store=True)
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection([('married','Married'),('single','Single')], string="Marital Status", tracking= True)
    partner_name = fields.Char(string="Partner Name")
    is_birthday = fields.Boolean(string="Birthday ?", compute="_compute_is_birthday")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', rec.id)])
    #    appoiintment_group = self.env['hospital.appointment'].read_group(domain=[], #('state', '=', 'done')
    #                                                                     fields=['patient_id'], groupby=['patient_id'])
    #    for appointment in appoiintment_group:
    #        patient_id = appointment.get('patient_id')
    #        patient_rec = self.browse(patient_id)
    #        patient_rec.appointment_count = appointment['patient_id_count']
    #        self -= patient_rec
    #        self.appointment_count = 0


    @api.constrains('date_of_birth')
    def _chech_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_("The entered date of birth is not acceptable !"))
            
    @api.ondelete(at_uninstall=False)
    def _check_appointment(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_("You can't delete a patient with appointments !"))


    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        # print("odoo mates", vals)
        return super(HospitalPatient, self).create(vals)
    
    def write(self, vals):
        if not self.ref and not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('hospital.patient')
        return super(HospitalPatient,self).write(vals)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0
        # today = date.today()
        # self.age = today.year - self.date_of_birth - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    @api.depends('age')
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)

    def _search_age(self, operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        start_of_year = date_of_birth.replace(day=1,month=1)
        end_of_year = date_of_birth.replace(day=31,month=12)
        return [('date_of_birth', '>=', start_of_year), ('date_of_birth', '<=', end_of_year)]

    def name_get(self):
        return [(record.id, "[%s]->%s" % (record.ref, record.name)) for record in self]
        # patient_list = []
        # for record in self:
        #     name = record.ref + ' ' + record.name
        #     patient_list.append((record.id, name))
        
        # return patient_list

    @api.depends('date_of_birth')
    def _compute_is_birthday(self):
        for rec in self:
            is_birthday = False
            if rec.date_of_birth:
                today = date.today()
                if today.day == rec.date_of_birth.day and today.month == rec.date_of_birth.month:
                    is_birthday = True
                rec.is_birthday = is_birthday

    def action_view_appointments(self):
        return{
            'name': _('Appointments'),
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form,calendar,activity',
            'context' : {'default_patient_id' : self.id},
            'domain' : [('patient_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',

        }
        