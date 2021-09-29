# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################
{
    'name': "AWB Prepaid Subscription",

    'summary': """
        Prepaid Subscription
        """,

    'description': """
        Prepaid Subscription
    """,

    'author': "Achieve Without Borders",

    'license': 'LGPL-3',

    'category': 'Localization',

    'version': '13.0.1.0.1',

    'depends': ['sale_subscription', 'awb_product_segmentation' ,'awb_subscriber_bill_automation'],

    'data': [
        'views/subscription_form_view.xml',
        'views/customer_portal_view.xml',
        'views/website_salecart_lines_view.xml',
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False

}
