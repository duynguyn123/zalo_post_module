import base64
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode
import requests
from odoo import models, fields, api # type: ignore
import logging
_logger = logging.getLogger(__name__)

class ZaloSchedule(models.Model):
    _name = 'zalo.schedule'
    _description = 'Zalo Post Schedule'

    zalo_post = fields.Many2one('zalo.post')
    schedule_date = fields.Datetime(related = 'zalo_post.schedule_date')
    post_status = fields.Char(related='zalo_post.post_status')
    #field realted status của post


    
    # @api.model
    # #ko chạy cron tab
    # def _auto_delete_expired_schedule(self):
    #     # Lấy ngày giờ hiện tại
    #     now = datetime.now()
    #     # Tìm các bản ghi có schedule_date đã đến hạn
    #     expired_schedules = self.search([('schedule', '<=', now)])
    #     # Xóa các bản ghi hết hạn
    #     expired_schedules.unlink()