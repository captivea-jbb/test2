{
    'name': 'Signup Extended Fields',
    'version': '12.0.1.0.2',
    'category': 'Website',
    'summary': 'Auth signup form with extra fields',
    'description': """
        This module add new fields to the website's sign up page

    """,
    'sequence': 1,
    'author': 'nathanqj',
    'website': 'http://captivea.us',
    'depends': ['website_form', 'auth_signup'],
    'data': [
        'views/auth_signup_extend_views.xml',
        'views/res_partner_view.xml',
        'data/data.xml',
    ],
    'qweb': [],
    'css': [],
    'js': [],
    'images': [
        'static/description/auth_signup_banner.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
