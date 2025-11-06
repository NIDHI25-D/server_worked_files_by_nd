from odoo import registry, SUPERUSER_ID, api
from odoo.tools import config
import threading
import subprocess
import logging
import os
from odoo.modules import get_module_path, get_resource_path
# import odoo = odoo.sql_db.db_connect('default').dbname
_logger = logging.getLogger("postgres")


def pre_init_input_query(cr):
    database_name = cr.registry.db_name
    print(database_name)
    _logger.info(f"{database_name}")

    # todo -- need to change user , password , host , port according to server and database change
    db_registry = registry(database_name)
    with db_registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info(f"{env}")
        t = threading.Thread(target=install_views, args=[(database_name)])
        _logger.info(f"{t}")
        t.start()
    with db_registry.cursor() as cr1:
        env1 = api.Environment(cr1, SUPERUSER_ID, {})
        t1 = threading.Thread(target=install_large_views, args=[(database_name)])
        t1.start()


def install_views(database_name):
    db_user = config.get('db_user')
    db_password = config.get('db_password')
    db_host = config.get('db_host') or '127.0.0.1'
    _logger.info(f"{db_host}")
    db_port = config.get('db_port') or 5432
    module_path = get_module_path('setu_product_view_by_vendor')
    _logger.info(f"{module_path}")
    role_password = 'M4rv3l123$'
    postgres_pass = ''
    odoo_14_pass = ''

    if database_name in ("mvsa_production", "mvsa_production_22_jun"):
        postgres_pass = 'mvSA1!2@3#4$5%6^7&8*9(10)/*+-RJ'
        odoo_14_pass = 'MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj'

    else:
        postgres_pass = 'yN8@K3pLmZ#vXr7Q$dS2fGtH!bR4jT'
        odoo_14_pass = 'MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj'

    # Grant
    subprocess.call(
        f"PGPASSWORD={postgres_pass} psql -h {db_host} -U {'postgres'} -d {database_name} < {module_path}/db_function/queries.sql",
        shell=True)
    _logger.info("create role")
    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} -c 'CREATE SCHEMA IF NOT EXISTS datastudio_reports AUTHORIZATION odoo14_datastudio';",
        shell=True)
    _logger.info("create schema")
    subprocess.call(
        f"PGPASSWORD={postgres_pass} psql -h {db_host} -U {'postgres'} -d {database_name} -c 'alter role odoo14_datastudio set search_path=datastudio_reports'; ",
        shell=True)
    _logger.info("alter role")
    subprocess.call(
        f"PGPASSWORD={postgres_pass} psql -h {db_host} -U {'postgres'} -d {database_name} -c 'grant odoo14_datastudio to odoo18'; ",
        shell=True)
    _logger.info("grant role")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} -c 'grant USAGE on SCHEMA datastudio_reports to odoo14_datastudio';",
        shell=True)
    _logger.info("usage rights")
    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} -c 'grant SELECT ON ALL tables in schema public TO odoo14_datastudio';",
        shell=True)
    _logger.info("right of all table.")

    # sql

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'}  -d {database_name} < {module_path}/db_function/get_journal_items_view.sql",
        shell=True)
    _logger.info("journal_items_view")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/product_template_stock_info.sql ",
        shell=True)
    _logger.info("product_template_stock_info")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'}  -d {database_name} < {module_path}/db_function/fleet_services_view.sql",
        shell=True)
    _logger.info("materialized_view_of_fleet_service")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/product_view_by_vendor.sql ",
        shell=True)
    _logger.info("product_view_by_vendor")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/sale_order_line_view.sql ",
        shell=True)
    _logger.info("sale_order_line_view")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'}  -d {database_name} < {module_path}/db_function/sale_order_line_invoice_rel_view.sql",
        shell=True)
    _logger.info("materialized_view_of_sale_order_line_invoice_rel")




def install_large_views(database_name):
    db_host = config.get('db_host') or '127.0.0.1'
    module_path = get_module_path('setu_product_view_by_vendor')
    odoo_14_pass = ''

    if database_name == "mvsa_production":
        postgres_pass = 'mvSA1!2@3#4$5%6^7&8*9(10)/*+-RJ'
        odoo_14_pass = 'MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj'
    else:
        postgres_pass = 'yN8@K3pLmZ#vXr7Q$dS2fGtH!bR4jT'
        odoo_14_pass = 'MVsa1!2@3#4$5%6^7&8*9(10)/*+-rj'

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/contact_view.sql ",
        shell=True)
    _logger.info("contact_view")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/product_tmpl_basic_info_view.sql ",
        shell=True)
    _logger.info("product_tmpl_basic_info_view")

    subprocess.call(
        f"PGPASSWORD={odoo_14_pass} psql -h {db_host} -U {'odoo18'} -d {database_name} < {module_path}/db_function/sale_order_view.sql ",
        shell=True)
    _logger.info("sale_order_view")

from . import model
