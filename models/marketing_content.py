
from odoo import models, fields, api # type: ignore

# Kế thừa Marketing Content
class MarketingContent(models.Model):
    _inherit="marketing.content"

    zalo_post = fields.One2many("zalo.post","content_id",string="Zalo post")






class YourModel(models.Model):
    _name = 'your.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enables Chatter

    name = fields.Char(string="Name", tracking=True)  # 'tracking=True' logs changes to Chatter
    description = fields.Text(string="Description", tracking=True)
    zalo_post = fields.One2many('zalo.post', 'youmodel')







    