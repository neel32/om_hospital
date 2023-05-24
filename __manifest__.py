{
    'name': 'Hospital Management System',
    'version': '1.0.0',
    'category': 'Hospital',
    'author': 'Odoo Mates',
    'summary': 'Hospital Management System',
    'sequence': '-100',
    'description' : """Hospital Management System""",
    'depends': ['mail','product','base'],
    'data' : [
        'security/ir.model.access.csv',
        'data/patient_tag_data.xml',
        'data/patient.tag.csv',
        'data/sequence_data.xml',
        'wizard/cancle_appointment.xml',
        'views/menu.xml',
        'views/patient.xml',
        'views/female_patient.xml',
        'views/male_patient.xml',
        'views/appointment.xml',
        'views/patient_tag_view.xml',
        'views/odoo_playground.xml',
        # 'views/res_config_settings_view.xml',
        # 'views/operation_view.xml',
    ],
    'demo' : [],
    'installable': True,
    'application': True,    
    'auto_install' : False,
    'license' : 'LGPL-3',
    
}