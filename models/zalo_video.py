import base64
import json
import logging
from urllib.parse import urlencode
import requests
from odoo import models, fields,_ , api # type: ignore
import logging
_logger = logging.getLogger(__name__)

class ZaloVideo(models.Model):  
    _name = 'zalo.video'
    _description = 'Zalo Video'

    # Gọi từ module account
    app_id = fields.Char(related="zalo_app_id.app_id", string='App ID')
    app_secret = fields.Char(related='zalo_app_id.app_secret', string='App Secret')
    access_token = fields.Char(related='zalo_app_id.access_token', string='Access Token')
    refresh_token = fields.Char(related='zalo_app_id.refresh_token', string='Refresh Token')
    token_expiration = fields.Datetime(related='zalo_app_id.token_expiration', string='Token Expiration')

    # Model gốc
    video_file = fields.Binary('Video File', required=False)  # Optional if video is not selected
    video_name = fields.Char('File Name', required=True)
    videoToken = fields.Char('Video Token')
    video_id = fields.Char('Video ID')

    #Liên kết với các model khác
    zalo_app_id = fields.Many2one('zalo.app', string = "Zalo Account", required=True)


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
        # Kiểm tra kết quả trả về
        if response.status_code == 200:
            return response.json()
        else:
            _logger.info('Error:', response.status_code, response.text)

    def action_upload_video(self):
        #Chạy api gửi video lên zalo cloud
        prepareVideo = self.prepare_video_upload()
        #gán token của video cho fields token
        self.videoToken = prepareVideo['data']['token']
        _logger.info(self.videoToken)

        return prepareVideo
    

    def verify_video_upload(self):
        url = "https://openapi.zalo.me/v2.0/article/upload_video/verify"
        
        # Prepare the payload
        headers = {
            'access_token': self.access_token,
            'token': self.videoToken
        }
        
        # Make the POST request
        response = requests.get(url, headers=headers)
        
        # Check for success
        if response.status_code == 200:
            return response.json()  # Return the JSON response
        else:
            return {
                'error': response.status_code,
                'message': response.text
            }


    def action_verify_video(self):
        verify = self.verify_video_upload()
        self.video_id = verify['data']['video_id']
        status_id = verify['data']['status']
        if status_id == 3:
            _logger.info("Not Done")
        if status_id == 1:
            _logger.info("Done")
        return verify
        
                
             
        



    

            


    

            
            
