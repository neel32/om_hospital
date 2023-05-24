import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _




class CancleAppointmentWizard(models.TransientModel):
    _name = "cancle.appointment.wizard"
    _description = "Cancle Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CancleAppointmentWizard, self).default_get(fields)
        res['date_cancle'] = datetime.date.today()
        if self.env.context.get('active_id'):
            res['appointment_id'] = self.env.context.get('active_id')
        return res

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment", domain=[('state', '=', 'draft')])
    reason = fields.Text(string="Reason", default='Test Reason')
    date_cancle = fields.Date(string="Cancellation date")

    def action_cancle(self):
        if self.appointment_id.booking_date == fields.Date.today():
            raise ValidationError(_('Sorry, cancellation is not allowed on the same day of booking!'))
        self.appointment_id.state = 'cancle'
        return{
           'type' : 'ir.actions.client',
           'view_mode' : 'form',
           'res_model' : 'cancle.appointment.wizard',
           'target' : 'new',
           'res_id' : self.id
       }

        # return{
        #     'type' : 'ir.actions.client',
        #     'tag' : 'reload',
        # }