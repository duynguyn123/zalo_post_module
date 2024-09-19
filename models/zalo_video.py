import base64
import logging
from urllib.parse import urlencode
import requests
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class ZaloVideo(models.Model):
    _name = 'zalo.video'
    _description = 'Zalo Video'

    # Gọi từ module account
    app_id = fields.Char(related="account_id.app_id", string='App ID')
    app_secret = fields.Char(related='account_id.app_secret', string='App Secret')
    access_token = fields.Char(related='account_id.access_token', string='Access Token')
    refresh_token = fields.Char(related='account_id.refresh_token', string='Refresh Token')
    token_expiration = fields.Datetime(related='account_id.token_expiration', string='Token Expiration')



    video_file = fields.Binary('Video File', required=False)  # Optional if video is not selected
    video_filename = fields.Char('File Name')
    videoToken = fields.Char('Video Token')
    video_id = fields.Char('Video ID')

    account_id = fields.Many2one('zalo.account', string = "Zalo Account")


    def prepare_video_upload(self):
        # URL của API
        url = 'https://openapi.zalo.me/v2.0/article/upload_video/preparevideo'

        # Mở file video để đọc dữ liệu nhị phân
        # with open(self.video_file, 'rb') as file:
            # Thực hiện POST request
        file = base64.b64decode(self.video_file)

        response = requests.post(
            url,
            headers={
                'access_token': self.access_token,
            },
            files={
                'file': (self.video_filename,file, 'video/mp4')
            }
        )

        # Kiểm tra kết quả trả về
        if response.status_code == 200:
            return response.json()
            
        else:
            print('Error:', response.status_code, response.text)

    def action_upload_video(self):
        prepareVideo = self.prepare_video_upload()
        if 'data' in prepareVideo:
            self.videoToken = prepareVideo.get('data', self.videoToken)
            _logger.info(prepareVideo['data'])
            new_Token = self.videoToken
            if isinstance(new_Token, dict):
                self.videoToken = new_Token.get('token', self.videoToken)

            # if 'token' in new_Token:
            #     self.videoToken = new_Token.get('token', self.videoToken)
            
            
            # _logger.info(new_Token)
        return prepareVideo
        
        
