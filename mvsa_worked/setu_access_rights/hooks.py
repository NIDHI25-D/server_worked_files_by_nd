import odoo.service.server as SERVER


def uninstall_hook(cr, registry):
    SERVER.restart()
