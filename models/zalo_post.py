from datetime import timedelta
import logging
from urllib.parse import urlencode
import requests
from odoo import models, fields, api # type: ignore
import logging
_logger = logging.getLogger(__name__)

class ZaloPost(models.Model):
    _name = 'zalo.post'
    _description = 'Zalo Post'

    # Gọi từ module zalo app
    app_id = fields.Char(related="zalo_app_id.app_id", string='App ID')
    app_secret = fields.Char(related='zalo_app_id.app_secret', string='App Secret')
    access_token = fields.Char(related='zalo_app_id.access_token', string='Access Token')
    refresh_token = fields.Char(related='zalo_app_id.refresh_token', string='Refresh Token')
    token_expiration = fields.Datetime(related='zalo_app_id.token_expiration', string='Token Expiration')
    zalo_account = fields.Many2one(related='zalo_app_id.zalo_account_id', string = "Zalo Account")

    # Gọi từ module video
    video_file = fields.Binary(related='videoID.video_file', string = "Video file")
    video_filename = fields.Char(related='videoID.name', string = 'File Name')
    videoToken = fields.Char(related='videoID.videoToken', string = 'Video Token')
    video_id = fields.Char(related='videoID.video_id', string="Video ID")

    # Gọi từ module marketing content
    name = fields.Text(related='content_id.content', string='Title')
    description = fields.Text(related='content_id.content', string='Description')
    image_ids = fields.One2many(related='content_id.image_ids')

    # model gốc
    schedule_date = fields.Datetime(string="Scheduled Date", help="Choose the date and time to schedule the post.")
    is_post_to_zalo = fields.Boolean("Post to Zalo", default=False)
    cover_url = fields.Char(string='Cover URL',compute="_depend_cover_url")
    is_posted = fields.Boolean(string="Is Post")
    have_video = fields.Boolean('Have Video', default=False)

    # Kết nối các models lại với nhau
    content_id = fields.Many2one('marketing.content'  , string='Marketing Content')
    marketing_product_id = fields.Many2one('marketing.product', string = "Product") 
    zalo_app_id = fields.Many2one('zalo.app', string = "Zalo App")
    account_id = fields.Many2one('zalo.account')
    videoID = fields.Many2one('zalo.video', string = "Video Name")



    # Lấy url hình ảnh đầu tiên của content
    @api.depends("image_ids")
    def _depend_cover_url(self):
        for record in self:
            if record.image_ids:  # Kiểm tra xem danh sách không rỗng
                if record.image_ids[0].id:  # Kiểm tra ID đã được xác định
                    record.cover_url = "http://mtk00.t4tek.tk/web/image?model=marketing.content.image&id=%d&field=image" % record.image_ids[0].id
                else:
                    record.cover_url = ""  # Rỗng nếu nếu ID không hợp lệ

    def create(self, vals):
        record = super(ZaloPost, self).create(vals)
        if record.is_post_to_zalo:
            record.action_post_feed()
            _logger.info("New")
        return record
    
    def write(self, vals):
        res = super(ZaloPost, self).write(vals)
        for record in self:
            if record.is_post_to_zalo and not record.is_posted:
                self.action_post_feed()
        return res
    

    @api.model
    def post_feed(self):
        # URL for the API endpoint
        url = "https://openapi.zalo.me/v2.0/article/create"
        _logger.info(f"access_token - {self.access_token}")
        
        # Headers including the access token
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "access_token": self.access_token
        }

        # Prepare the body based on the user's selection of content type
        body_content = [
            {
                "type": "video",
                "video_id": self.video_id
            },
            {
                "type": "text",
                "content": self.description
            },
            {
                "type": "image",
                "url": self.cover_url
            }]
        
        # if self.have_video:
        #     body_content.append({
        #         "type": "video",
        #         "video_id": self.video_id
        #     },
        #     {
        #         "type": "text",
        #         "content": self.description
        #     },
        #     {
        #         "type": "image",
        #         "url": self.cover_url
        #     })
        # elif self.have_video == False:
        #     body_content.append({
        #         "type": "text",
        #         "content": self.description
        #     },
        #     {
        #         "type": "image",
        #         "url": self.cover_url
        #     })

        # Payload containing app_id, app_secret, message, and link
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "type": "normal",
            "title": self.name,
            "author": "News",
            "cover": {
                "cover_type": "photo",
                "photo_url": self.cover_url,
                "status": "show"
            },
            "description": self.description,
            "body": body_content,
            "status": "show",
            "comment": "show"
        }

        # Send POST request with headers and JSON payload
        response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            self.is_posted = True
            return response.json()  # Return the JSON response
        else:
            response.raise_for_status()  # Raise an exception for any errors

    def action_post_feed(self):
        response_feed = self.post_feed()
        return response_feed
    
    @api.model
    def schedule_post_feed(self):
        # Fetch records where the scheduled date has passed and the post has not been made
        records = self.search([('schedule_date', '<=', fields.Datetime.now()), ('is_posted', '=', False)])
        
        for record in records:
            try:
                record.action_post_feed()  # Call the post feed action
                record.is_posted = True  # Mark as posted
                _logger.info(f"Successfully posted feed for record {record.id}")

                self.env.user.notify_info(
                    message=f"Successfully posted feed for record {record.id}",
                    title="Success",
                    sticky=False
                )
            except Exception as e:
                _logger.error(f"Failed to post feed for record {record.id}: {e}")
    

    


    
    
        




