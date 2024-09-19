from datetime import timedelta
import logging
from urllib.parse import urlencode
import requests
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ZaloPost(models.Model):
    _name = 'zalo.post'
    _description = 'Zalo Post'

    # Gọi từ module account
    app_id = fields.Char(related="account_id.app_id", string='App ID')
    app_secret = fields.Char(related='account_id.app_secret', string='App Secret')
    access_token = fields.Char(related='account_id.access_token', string='Access Token')
    refresh_token = fields.Char(related='account_id.refresh_token', string='Refresh Token')
    token_expiration = fields.Datetime(related='account_id.token_expiration', string='Token Expiration')


    # Gọi từ module video
    video_filename = fields.Char(related='videoID.video_filename', string = 'File Name')
    videoToken = fields.Char(related='videoID.videoToken', string = 'Video Token')
    video_id = fields.Char(related='videoID.video_id', string="Video ID")


    # model gốc
    schedule_date = fields.Datetime(string="Scheduled Date", help="Choose the date and time to schedule the post.")
    title = fields.Char(string='Title')
    description = fields.Text(string='Description')
    cover_url = fields.Char(string='Cover URL')
    body_content = fields.Html(string='Body Content')
    is_posted = fields.Boolean(string="Is Post")


    # Kết nối các models lại với nhau
    zalo_post_id = fields.Many2one('zalo.video', string = "Zalo Post")
    content_id = fields.Many2one('marketing.content'  , string='Marketing Content')
    marketing_product_id = fields.Many2one('marketing.product', string = "Product") 
    account_id = fields.Many2one('zalo.account', string = "Zalo Account")
    videoID = fields.Many2one('zalo.video', string = "Zalo Video Upload")
    content = fields.Many2one('marketing.content', string = "Marketing Content")
    
    
    # # Add selection for the content type
    # body_type = fields.Selection([
    #     ('text', 'Text'),
    #     ('image', 'Image'),
    #     ('video', 'Video')
    # ], string='Body Type', default='text')

    # # Additional fields based on body type
    # text_content = fields.Text(string='Text Content')
    # image_url = fields.Char(string='Image URL')
    # video_url = fields.Char(string='Video URL')


    @api.onchange('content_id')
    def _onchange_content_id(self):
        """Lấy giá trị title và content từ module gốc khi content_id thay đổi."""
        if self.content_id:
            self.title = self.content_id.content
            self.description = self.content_id.content

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
        body_content = [{
                "type": "text",
                "content": self.description or "Default text content"
            }]
        
        # if self.body_type == 'text':
        #     body_content.append({
        #         "type": "text",
        #         "content": self.text_content or "Default text content"
        #     })
        # elif self.body_type == 'image':
        #     body_content.append({
        #         "type": "image",
        #         "url": self.image_url or "https://img.freepik.com/free-vector/gradient-dynamic-blue-lines-background_23-2148995756.jpg",
        #         "caption": "Image Caption"
        #     })
        # elif self.body_type == 'video':
        #     body_content.append({
        #         "type": "video",
        #         "url": self.video_url or "https://example.com/default-video.mp4",
        #         "caption": "Video Caption"
        #     })

        # Payload containing app_id, app_secret, message, and link
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
            "type": "normal",
            "title": self.title or "News",
            "author": "News",
            "cover": {
                "cover_type": "photo",
                "photo_url": self.cover_url or "https://img.freepik.com/free-vector/gradient-dynamic-blue-lines-background_23-2148995756.jpg",
                "status": "show"
            },
            "description": [
                {
                    "type": "image",
                    "url": self.cover_url or "https://img.freepik.com/free-vector/gradient-dynamic-blue-lines-background_23-2148995756.jpg",
                    "caption": "News"
                }
            ],
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


    # def schedule_post_feed(self):
    #     # Fetch records with a schedule time that is due
    #     records = self.search([('next_run_date', '<=', fields.Datetime.now())])
    #     for record in records:
    #         record.action_post_feed()
    #         # Update the next run date, e.g., to run again in 1 hour
    #         record.next_run_date = fields.Datetime.now() + timedelta(hours=1)

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
            except Exception as e:
                _logger.error(f"Failed to post feed for record {record.id}: {e}")
    

    


    
    
        




