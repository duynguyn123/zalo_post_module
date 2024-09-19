
from odoo import models, fields, api # type: ignore

# Kế thừa Marketing Content
class MarketingContent(models.Model):
    _inherit="marketing.content"

    zalo_post = fields.One2many("zalo.post","content_id",string="Zalo post")

    @api.model
    def create(self, vals):
        # Tạo bản ghi mới cho model 'MarketingContent'
        record = super(MarketingContent, self).create(vals)

        # Giả sử bạn có một bản ghi 'zalo.post' đã tồn tại, cần gán giá trị
        zalo_post = self.env['zalo.post'].search([('id', '=', record.id)], limit=1)
        
        if zalo_post:
            # Gán giá trị mới
            zalo_post.write({
                "description": record.content,  
                "title": record.content
            })
        return record

# Kế thừa Marketing Product
class MarketingProduct(models.Model):
    _inherit="marketing.product"

    zalo_post = fields.One2many("zalo.post","marketing_product_id",string="Zalo post")


    