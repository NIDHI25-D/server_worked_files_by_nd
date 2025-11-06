# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
from os.path import join, dirname, realpath
from odoo.tools.sql import SQL
_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _load_sepomex_catalog(env)


def _load_sepomex_catalog(env):
    csv_file_path = join(dirname(realpath(__file__)), 'data', 'sepomex.csv')
    csv_file = open(csv_file_path, encoding='latin1')
    env.cr.copy_from(csv_file, 'sepomex_res_colony_csv', sep='|', columns=('postal_code', 'colony', 'l10n_mx_edi_city_id'))

    env.cr.execute(SQL("""
            INSERT INTO sepomex_res_colony (postal_code, name, city_id)
            SELECT csv.postal_code, csv.colony, data.res_id
            FROM sepomex_res_colony_csv AS csv, ir_model_data AS data
            WHERE csv.l10n_mx_edi_city_id = data.name
        """))

    env.cr.execute(SQL("""
        UPDATE sepomex_res_colony
        SET display_name = sepomex_res_colony.postal_code || ', Col. ' || sepomex_res_colony.name || ', ' || rc.name || ', ' || rcs.name || ' (' || rc2.code || ')'
        FROM res_city rc, res_country_state rcs, res_country rc2 
        WHERE sepomex_res_colony.city_id = rc.id AND rcs.id = rc.state_id AND rc.country_id = rc2.id
    """))
