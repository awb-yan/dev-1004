# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Product Segmentation",

    'summary': """
        Product Segmentation
        """,

    'description': """
        Extension Odoo Apps
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.4.3',

    'depends': ['sale_management', 'sale_subscription'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/plan_type_view.xml',
    ],
}