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
    # app_id = fields.Char(related="zalo_app_id.app_id", string='App ID')
    # app_secret = fields.Char(related='zalo_app_id.app_secret', string='App Secret')
    # access_token = fields.Char(related='zalo_app_id.access_token', string='Access Token')
    # refresh_token = fields.Char(related='zalo_app_id.refresh_token', string='Refresh Token')
    # token_expiration = fields.Datetime(related='zalo_app_id.token_expiration', string='Token Expiration')

    zalo_post = fields.Many2one('zalo.post')
    schedule = fields.Datetime(related = 'zalo_post.schedule_date')
    videoToken = fields.Char(related='zalo_post.videoToken')
    status = fields.Char(related='zalo_post.status')
    video_id = fields.Char(related='zalo_post.video_id')
    video_name = fields.Char(related='zalo_post.video_name')

    #token video
    #verify video
    #unlink khi đã xong

    #Liên kết với các model khác
    # zalo_app_id = fields.Many2one('zalo.app', string = "Zalo Account", required=True)
