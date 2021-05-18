{
    'name': 'Sales order multi lots selection with available product quantity and restirct nonstockable product',
    'version': '12.0.2',
    'category': 'Sales Management',
    'summary': 'Using this module you can select multiple lot in sale order line and you can only select lot number if product lot number is avaialble  with  Lot quantity',
    'description': """ Using this module you can select multiple lot in sale order line and you can only select lot number if product lot number is avaialble  with  Lot quantity.
    """,
    'price': 10,
    'currency': 'EUR',
    "author" : "MAISOLUTIONSLLC",
    'sequence': 1,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    'license': 'OPL-1',
    'depends': ['sale_management','sale_stock'],
    # "live_test_url" : "",
    'data': [
        'views/sale_view.xml',
        'report/sale_report_templates.xml',
    ],
    'qweb': [
        ],
    'images': ['static/description/main_screenshot.png'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
