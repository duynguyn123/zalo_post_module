from urllib.parse import urlencode
import requests
from odoo import models, fields, _ # type: ignore
import logging
_logger = logging.getLogger(__name__)
from datetime import timedelta


class ZaloAccount(models.Model):
    _name = 'zalo.account'
    _description = 'Zalo Offical Account'

    is_favorite = fields.Boolean(string="Favorite", default=False, tracking=True)
    name = fields.Char('Tên tài khoản', required=True)
    account_id = fields.Char('App ID', required=True)
    account_type = fields.Char('Danh mục', required=True)
    image_url = fields.Char('Url Image')



