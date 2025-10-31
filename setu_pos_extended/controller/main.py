from odoo import http
from odoo.http import request

class SetuPosExtended(http.Controller):

	@http.route('/setu_pos_extended/get_sales_teams', type='json')
	def get_sales_teams(self, **kw):
		""" This webhook is called when the extraction server is done processing a request."""
		query = f"""
		SELECT 
			id, name -> 'en_US' as label
		FROM
			crm_team;
		"""
		request.env.cr.execute(query)
		sales_team_list = request.env.cr.fetchall()
		
		sales_teams = [{"id" :x[0], "item": x[0], "label": x[1]} for x in sales_team_list]	
		return sales_teams
