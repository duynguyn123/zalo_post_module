import base64
import logging
import requests
from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import UserError, ValidationError # type: ignore
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class ZaloPost(models.Model):
    _name = 'zalo.post'
    _description = 'Zalo Post'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Ensure inheritance

    #Model zalo.app
    zalo_account = fields.Many2one(related='zalo_app_id.zalo_account_id', string = "Zalo Account")
    access_token = fields.Char(related='zalo_app_id.access_token', string='Access Token')
    name = fields.Text(related='content_id.content', string='Title')


    schedule_date = fields.Datetime(string="Scheduled Date", help="Choose the date and time to schedule the post.")
    is_post_to_zalo = fields.Boolean("Post now", default=False)
    cover_url = fields.Char(string='Cover URL',compute="_depend_cover_url")
    is_posted = fields.Boolean(string="Is Post")
    no_video = fields.Boolean('No Video', default=False)
    post_message_respond = fields.Char('Message Respond')
    post_status = fields.Char(string='Post Status')

    #Video 
    video_message_respond = fields.Char('Video Message Respond')
    video_file = fields.Binary('Video File', required=False)  # Optional if video is not selected
    video_name = fields.Char('File Name',default="New video")
    videoToken = fields.Char('Video Token', default="None")
    video_id = fields.Char('Video ID')
    status = fields.Char('Status')
    video_type = fields.Selection([
        ('cover_only', 'For cover'),
        ('content_only', 'For content'),
        ('cover_and_content', 'For cover and content'),

    ], string='This video for')


    #Model marketing.content
    image_ids = fields.One2many(related='content_id.image_ids')

    # Kết nối các models lại với nhau
    content_id = fields.Many2one('marketing.content'  , string='Marketing Content')
    zalo_app_id = fields.Many2one('zalo.app', string = "Zalo App")
    account_id = fields.Many2one('zalo.account')
    youmodel = fields.Many2one('your.model')

    



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
        now = datetime.now()
        
        record = super(ZaloPost, self).create(vals)

        if record.no_video:
            record.post_status = "Ready"
        else:
            record.post_status = " Waiting"
            
        if record.is_post_to_zalo:
            try:
                record.write({'schedule_date': now})
                record.action_post_feed()
            except Exception as e:
                _logger.error(f"Error posting to Zalo: {e}")
            
        #Lưu vào schedule post
        zalo_schedule = self.env["zalo.schedule"].create({
            "zalo_post": record.id
        })
        


        #Nếu có video
        if record.no_video == False:
            zalo_video = self.env["zalo.video"].create({
                "zalo_post": record.id,
                "schedule": now
            })
            record.action_upload_and_verify_video()
            zalo_video_converted = self.env["zalo.videoconvert"].create({
                "zalo_post": record.id,
                "videoToken": record.videoToken
            })
        return record
    
    def write(self, vals):
        now = datetime.now()
        for record in self:

             # Prevent recursive write calls by checking if the value is already set
            if record.is_post_to_zalo and not record.is_posted and not record.schedule_date:
                vals.update({"schedule_date": now})
                # self.action_post_feed()

        res = super(ZaloPost, self).write(vals)
        for record in self:
            if record.is_post_to_zalo:
                self.env["zalo.schedule"].create({
                    "zalo_post": record.id
                })

        # Nếu có video, tạo bản ghi zalo.video với ngày hiện tại
        if record.no_video == False and record.video_name != "New":
            self.env["zalo.video"].create({
                "zalo_post": record.id,
                "schedule": now
            })
            record.action_upload_and_verify_video()
            zalo_video_converted = self.env["zalo.videoconvert"].create({
                "zalo_post": record.id,
                "videoToken": record.videoToken
            })
        return res
    

    @api.model
    def post_feed(self):
        # URL for the API endpoint
        url = "https://openapi.zalo.me/v2.0/article/create"
        _logger.info(f"access_token - {self.zalo_app_id.access_token}")
        
        # Headers including the access token
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "access_token": self.zalo_app_id.access_token
        }

        # Prepare the body based on the user's selection of content type
        body_content = [
            {
                "type": "text",
                "content": self.content_id.content
            },
            {
                "type": "image",
                "url": self.cover_url
            }]
        

        # Payload containing app_id, app_secret, message, and link
        payload = {
            "app_id": self.zalo_app_id.app_id,
            "app_secret": self.zalo_app_id.app_secret,
            "type": "normal",
            "title": self.content_id.content,
            "author": "News",
            "cover": {
                "cover_type": "photo",
                "photo_url": self.cover_url,
                "status": "show"
            },
            "description": self.content_id.content,
            "body": body_content,
            "status": "show",
            "comment": "show"
        }

        if self.video_type == 'cover_only':
            payload = {
                "app_id": self.zalo_app_id.app_id,
                "app_secret": self.zalo_app_id.app_secret,
                "type": "normal",
                "title": self.content_id.content,
                "author": "News",
                "cover": {
                    "cover_type": "video",
                    "cover_view": "horizontal",
                    "video_id": self.video_id,
                    "status": "show"
                },
                "description": self.content_id.content,
                "body": body_content,
                "status": "show",
                "comment": "show"
            }

        elif self.video_type == 'content_only':
            body_content = [
            {
                "type": "video",
                "video_id": self.video_id,
            },
            {
                "type": "text",
                "content": self.content_id.content
            },
            {
                "type": "image",
                "url": self.cover_url
            }]

        elif self.video_type == 'cover_and_content':
            body_content = [
            {
                "type": "video",
                "video_id": self.video_id,
            },
            {
                "type": "text",
                "content": self.content_id.content
            },
            {
                "type": "image",
                "url": self.cover_url
            }]

            payload = {
                "app_id": self.zalo_app_id.app_id,
                "app_secret": self.zalo_app_id.app_secret,
                "type": "normal",
                "title": self.content_id.content,
                "author": "News",
                "cover": {
                    "cover_type": "video",
                    "cover_view": "horizontal",
                    "video_id": self.video_id,
                    "status": "show"
                },
                "description": self.content_id.content,
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
        if 'message' in response_feed:
            self.post_message_respond = response_feed['message']
            _logger.info(self.post_message_respond)

        if response_feed['error'] != 0:
            self.post_status = 'Error'
            raise UserError(f"Đăng bài không thành công! Lỗi: {self.post_message_respond}")   
        
        self.post_status = 'Success'
            
        return response_feed
    
    @api.model
    def schedule_post_feed(self):
        # Fetch records where the scheduled date has passed and the post has not been made
        now = datetime.now()
        records = self.env["zalo.schedule"].search([
            ('schedule_date', '<=', now),
            ('post_status', '=', 'Ready')
        ])
        
        for record in records:
            zalo_post = record.zalo_post
            try:
                zalo_post.action_post_feed()  # Call the post feed action
                zalo_post.is_posted = True  # Mark as posted
                _logger.info(f"Successfully posted feed for record {zalo_post.id}")
                
                # Delete the schedule record after successful posting
                record.unlink()
                _logger.info(f"Deleted schedule record {record.id}")

            except Exception as e:
                # Log the error and raise a popup to notify the user
                _logger.error(f"Failed to post feed for record {zalo_post.id}: {e}")
                raise UserError(_(f"Failed to post feed for record {zalo_post.id}: {e}"))
            
    

    

    def prepare_video_upload(self):
        # URL của API
        url = 'https://openapi.zalo.me/v2.0/article/upload_video/preparevideo'
        # Thực hiện POST request
        file = base64.b64decode(self.video_file)
        response = requests.post(
            url,
            headers={
                'access_token': self.access_token,
            },
            files={
                'file': (self.video_name,file, 'video/mp4')
            }
        )
        _logger.info( f"zalo app access = {self.access_token}")
        # Kiểm tra kết quả trả về
        if response.status_code == 200:
            return response.json()
        else:
            _logger.info('Error:', response.status_code, response.text)

    def action_upload_video(self):

        #Chạy api gửi video lên zalo cloud
        prepareVideo = self.prepare_video_upload()

        #gán token của video cho fields token
        _logger.info(f"API Response: {prepareVideo}")

        #Hiển thị thông tin lỗi 
        if 'message' in prepareVideo:
            self.video_message_respond = prepareVideo['message']

        if prepareVideo ['error'] !=0:
            _logger.info(f"Unexpected API response: {prepareVideo}")
            raise UserError(
            f"Upload video không thành công! Lỗi: {self.video_message_respond}")

        # Check if 'data' key exists to avoid KeyError
        if 'data' in prepareVideo and 'token' in prepareVideo['data']:
            self.videoToken = prepareVideo['data']['token']
        else:
            raise UserError(
            f"Không tìm thấy video token! Lỗi: {self.video_message_respond}")
        return prepareVideo
    

    def verify_video_upload(self):
        url = "https://openapi.zalo.me/v2.0/article/upload_video/verify"
        
        # Prepare the payload
        headers = {
            'access_token': self.zalo_app_id.access_token,
            'token': self.videoToken
        }
        
        # Make the POST request
        response = requests.get(url, headers=headers)
        
        # Check for success
        if response.status_code == 200:
            return response.json()  # Return the JSON `response`
        else:
            return {
                'error': response.status_code,
                'message': response.text
            }


    def action_verify_video(self):
        verify = self.verify_video_upload()
        if 'message' in verify:
            self.video_message_respond = verify['message']
            _logger.info(self.video_message_respond)

        if verify['error'] == 0:
            self.video_id = verify['data']['video_id']
            videoStatus = verify['data']['status']
            if videoStatus == 3:
                self.status = "Being converted"
                _logger.info('Video is being converted')
                
            elif videoStatus == 1:
                self.status = "Ready"
                self.post_status = "Ready"
                _logger.info('Video is ready')
        
        else:
            message_respond = verify['message']
            raise UserError(f"Lỗi: {message_respond}")
            
        return verify
    
    def schedule_video(self):
            records = self.env["zalo.videoconvert"].search([])
            for record in records:
                zalo_post = record.zalo_post

                #Kiểm tra video upload
                #update trạng thái nếu thành công
                zalo_post.action_verify_video()

                #xóa bảng ghi
                zalo_post.unlink()


    def action_upload_and_verify_video(self):
        # First, upload the video
        prepareVideo = self.action_upload_video()
        
        # Then, verify the uploaded video
        verifyVideo = self.action_verify_video()

        return {
            'prepareVideo': prepareVideo,
            'verifyVideo': verifyVideo,
        }
    
        




