
from odoo import models, fields, api # type: ignore

# Kế thừa Marketing Content
class MarketingContent(models.Model):
    _inherit="marketing.content"

    zalo_post = fields.One2many("zalo.post","content_id",string="Zalo post")



# Kế thừa Marketing Product
class MarketingProduct(models.Model):
    _inherit="marketing.product"

    zalo_post = fields.One2many("zalo.post","marketing_product_id",string="Zalo post")







    