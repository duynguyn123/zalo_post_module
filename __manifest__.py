{
    'name': 'Zalo Marketing Module v1',
    'version': '1.0',
    'summary': 'Post articles to Zalo Official Account (OA)',
    'author': 'Your Name',
    'category': 'Social',
    'depends': ['base','website_sale','MarketingContent'],
    'data': [
        # 'security/security.xml',
        'views/zalo_post_views.xml',
        'data/cron_new_token.xml',
        'data/cron_post_feed.xml',
        'views/zalo_app_view.xml',
        'views/zalo_account_view.xml',
        'views/zalo_post_video.xml',
        'views/inherit_marketing_content.xml',
        'security/ir.model.access.csv',

        'views/menu_view.xml',

    ],
    'installable': True,
    'application': True,
}
