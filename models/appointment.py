from odoo.exceptions import UserError
import random
from odoo.exceptions import ValidationError
from odoo import models, fields, api,  _
from datetime import datetime

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT





class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="ref"
    _order = "ref"

    # name = fields.Char(string='Appointment ID', required=False, copy=False, readonly=True,
    #                    index=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(comodel_name='hospital.patient', string="Patient", ondelete='cascade', trim=True) #ondelete='restrict' not delete Patient before delete a appointment 
    gender = fields.Selection(related='patient_id.gender')                                              #ondelete='cascade' will delete Patient and also delete a appointment     
    appointment_time = fields.Datetime(string='Appointment Time', default=fields.Datetime.now)
    booking_date = fields.Date(string='Booking Date', default=fields.Date.context_today)
    ref = fields.Char(string="Reference", help="Reference from patient record")
    prescription = fields.Html(string='Prescription')
    priority = fields.Selection([
        ('0', 'Not'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'Average'),
        ('4', 'High'),
        ('5', 'Very High')], string="priority")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_consultation', 'In Consultation'),
        ('done', 'Done'),
        ('cancle', 'Canclled')], default='draft', string="status", required=True)
    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=True)
    pharmacy_line_ids = fields.One2many('appointment.pharmacy.lines', 'appointment_id', string='Pharmacy Lines')
    hide_sales_price = fields.Boolean(string="Hide Sales Price")
    progress = fields.Integer(string="Progress", compute = '_compute_progress')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    duration = fields.Float(string="Duration", compute="_compute_duration", store=True)
    company_id = fields.Many2one('res.company', string='Comapny', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    amount_total = fields.Monetary(string="Total", compute="_compute_amount_total", currency_field="currency_id")


    @api.depends('pharmacy_line_ids.price_subtotal')
    def _compute_amount_total(self):
        for appointment in self:
            amount_total = sum(appointment.pharmacy_line_ids.mapped('price_subtotal'))
            appointment.amount_total = amount_total


    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
    #     res = super(HospitalAppointment, self). create(vals)
    
    #     sl_no = 0
    #     for line in res.pharmacy_lines_ids:
    #         sl_no += 1
    #         line.sl_no = sl_no
    #     return res
    
    def write(self, values):
        res = super(HospitalAppointment, self).write(values)
        sl_no = 0
        for line in self.pharmacy_line_ids:
            sl_no += 1
            line.sl_no = sl_no
        return res
    
    

    # @api.model
    # def create(self, vals):
    #     # overriding the create method to add the sequence
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
    #     result = super(HospitalAppointment, self).create(vals)
    #     return result

    # def write(self, vals):
    #     if not self.ref and not vals.get('name'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
    #     return super(HospitalAppointment,self).write(vals)

    # @api.model
    # def write(self, vals):
    #     # overriding the write method of appointment model
    #     res = super(HospitalAppointment, self).write(vals)
    #     print("Test write function")
    #     # do as per the need
    #     return res

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                start_date = datetime.strptime(record.start_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end_date = datetime.strptime(record.end_date, DEFAULT_SERVER_DATETIME_FORMAT)

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("You cannot delete appointment with 'Done' status !"))
        return super(HospitalAppointment, self).unlink()
    
    @api.onchange('patient_id')
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_notification(self):
        action = self.env.ref('om_hospital.action_hospital_patient')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('The following replenishment order has been generated'),
                'message': '%s',
                'links': [{
                    'label': self.patient_id.name,
                    'url': f'#action={action.id}&id={self.patient_id.id}&model=hospital.patient]',
                }],
                'type': 'success',
                'sticky': True,
                'next' : {
                    'type' : 'ir.actions.act_window',
                    'res_model' : 'hospital.patient',
                    'res_id' : self.patient_id.id,
                    'views' : [(False, 'form')],
                }
            }
    }


    def action_test(self):
        return{
            'type' : 'ir.actions.act_url',
            'target' : 'self',
            'url' : 'https://www.google.com/'
        }
    
    def action_in_consultation(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'in_consultation'
    
    def action_done(self):
        for rec in self:
            rec.state = 'done'
        return {
            'effect' : {
                'fadeout' : 'slow',
                'message' : 'Done',
                'type' : 'rainbow_man',
            }
        }
    
    def action_cancle(self):
        action = self.env.ref('om_hospital.action_cancle_appointment').read()[0]
        for rec in self:
            rec.state = 'cancle'
        return action
    
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

        
    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(_("Missing Phone Number in Patient Record"))
        message = 'Hii %s , Your Appointment number is: %s, Thank you' % (self.patient_id.name, self.ref)
        whatsapp_api_url = 'https://api.whatsapp.com/send?phone=%s&text=%s' % (self.patient_id.phone, message)
        
        self.message_post(body=message, subject='Whatsapp Message')
        
        return{
            'type' : 'ir.actions.act_url',
            'target' : 'new',
            'url' : whatsapp_api_url
        }

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'draft':
                progress = random.randrange(0,25)
            elif rec.state == 'in_consultation':
                progress = random.randrange(25,75)
            elif rec.state == 'done':
                progress = 100
            else:
                progress = 0
            rec.progress = progress
    
    
class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    sl_no = fields.Integer(string="SNO.")
    product_id = fields.Many2one('product.product', required=True)
    price_unit = fields.Float(related='product_id.list_price', digits='Product Price')
    qty = fields.Integer(string='Quantity', default=1)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment ID')
    currency_id = fields.Many2one('res.currency', related="appointment_id.currency_id")
    price_subtotal = fields.Monetary(string="Subtotal", compute="_compute_price_subtotal", currency_field="currency_id")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.price_unit = self.product_id.lst_price

    @api.depends('price_unit', 'qty')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.qty




















    # class HospitalAppointment(models.Model):
#     _name = "hospital.appointment"
#     _inherit = ['mail.thread','mail.activity.mixin']
#     _description = "Hospital Appointment"
#     _rec_name="patient_id"


# from odoo import api, models, fields, _
# from odoo.exceptions import ValidationError
# from lxml import etree
# import pytz


    # name = fields.Char(string='Appointment ID', required=True, copy=False, readonly=True,
    #                    index=True, default=lambda self: _('New'))
    # patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    # doctor_id = fields.Many2one('hospital.doctor', string='Doctor')
    # notes = fields.Text(string="Registration Note")
    # # How to Create One2Many Field
    # # https://www.youtube.com/watch?v=_O_tNBdg3HQ&list=PLqRRLx0cl0hoJhjFWkFYowveq2Zn55dhM&index=34
    # appointment_date = fields.Date(string='Date')
    # partner_id = fields.Many2one('res.partner', string="Customer")
    # state = fields.Selection([
    #         ('draft', 'Draft'),
    #         ('confirm', 'Confirm'),
    #         ('done', 'Done'),
    #         ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, default='draft')

    # @api.model
    # def create(sel, vals):
    #     vals['name'] = self,env['ir.sequence'] .next_by_code('hospital.appointment')
    #     return super(HospitalAppointment, self). create(vals)