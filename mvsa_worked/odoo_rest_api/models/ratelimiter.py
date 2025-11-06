import time
from collections import defaultdict
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RateLimiter(models.Model):
    _name = 'rate.limiter'
    _description = 'Rate Limiter'

    api_name = fields.Char('API Name')
    key = fields.Char('Key')
    timestamp = fields.Float('Timestamp')

    @staticmethod
    def _get_limit_and_period(api_name, env):
        """
           Author: nidhi@setuconsulting
           Date: 25/11/24
           Task: Rest api
           Purpose: This method is used to get limit and period from the settings.
           Convert into seconds
        """
        limit = int(env['ir.config_parameter'].sudo().get_param(f'odoo_rest_api.limit_for_{api_name}'))
        minutes = int(env['ir.config_parameter'].sudo().get_param(f'odoo_rest_api.minutes_for_{api_name}'))
        period = minutes * 60 if minutes else 60  # Default to 1 minutes (60 seconds)
        return limit if limit else 1, period

    @staticmethod
    def is_rate_limited(key, api_name, env):
        """
           Author: nidhi@setuconsulting
           Date: 25/11/24
           Task: Rest api
           Purpose: This method is used to give error when the limit of API is completed, if the limit is not reached then it will create
                    the record in the rate.limiter and will allow the API to go upto the limit
        """
        limit, period = RateLimiter._get_limit_and_period(api_name, env)
        current_time = time.time()
        # Fetch all requests made by the key for the given API
        request_times = env['rate.limiter'].sudo().search([
            ('api_name', '=', api_name),
            ('key', '=', key),
            ('timestamp', '>', current_time - period)
        ])

        # If the number of requests exceeds the limit, rate limit is triggered
        if len(request_times) >= limit:
            return True

        # Store the new request timestamp in the database
        env['rate.limiter'].sudo().create({
            'api_name': api_name,
            'key': key,
            'timestamp': current_time,
        })

        return False

    @staticmethod
    def remaining_requests(key, api_name, env):
        """
           Author: nidhi@setuconsulting
           Date: 25/11/24
           Task: Rest api
           Purpose: This method is used to get the count of remaining API.
        """
        limit, period = RateLimiter._get_limit_and_period(api_name, env)
        current_time = time.time()

        # Fetch all requests made by the key for the given API. This logic will also search the rate.limit per user and keep the record by timestamp
        request_times = env['rate.limiter'].sudo().search([
            ('api_name', '=', api_name),
            ('key', '=', key),
            ('timestamp', '>', current_time - period)
        ])

        # Return the number of remaining requests
        return max(0, limit - len(request_times))

    @staticmethod
    def get_rate_limiter(api_name, env):
        return RateLimiter

    @staticmethod
    def clear_stale_records(env,api_name=None):
        """
           Author: nidhi@setuconsulting
           Date: 25/11/24
           Task: Rest api
           Purpose: Clear outdated rate limiter records dynamically.
                    This ensures only records that are out of the current period are removed.
        """
        domain = []
        if api_name:
            domain.append(('api_name', '=', api_name))
        stale_records = env['rate.limiter'].sudo().search(domain)

        if stale_records:
            stale_records.unlink()
            _logger.info(f"Cleared stale records for API: {api_name}")
