from odoo import models, fields, api, _
from datetime import timedelta
from odoo.tools.safe_eval import safe_eval
import time
from odoo.tools.float_utils import float_round
import logging

_logger = logging.getLogger(__name__)


class ExportForecastWizard(models.TransientModel):
    _inherit = 'forecast.export.wizard'

    purchase_order_based_on_doi_id = fields.Many2one(
        comodel_name='forecast.days.config',
        string='Purchase Order Based On Doi',
        help='Select one period to use for the Purchase Order.',
    )
    import_file_forecast_wizard_for_margin = fields.Binary(string="Import XLSX File", required=False)

    def _apply_triggers_to_lines(self, forecast_lines):
        # Rules in report
        ForecastLine = self.env['forecast.report.line']
        trigger_main = self.env['trigger.main'].search([])
        triggered_lines = ForecastLine.browse()

        for line in forecast_lines:
            rule_applied = False
            for triggermain in trigger_main:
                _logger.info("Processing Trigger Main: %s", triggermain.name)
                main_domain = safe_eval(triggermain.trigger_main_domain or '[]')
                if main_domain and not line.filtered_domain(main_domain):
                    _logger.info("Trigger Main domain not satisfied for line %s -> skipping", line.id)
                    continue  # Skip this trigger.main and move to next

                # Loop oDver threshold lines of this trigger main
                for threshold in triggermain.threshold_line_ids:  # ← tls is trigger.threshold.line
                    _logger.info("Evaluating Threshold Line: %s ", threshold.id)

                    if threshold.condition_type_forecast == 'rules_by_domain':
                        _logger.info("🔍 Condition type: rules_by_domain for %s", threshold.threshold_name)

                        # Evaluate the threshold domain
                        threshold_domain = safe_eval(threshold.threshold_domain or '[]')
                        domain_match = line.filtered_domain(threshold_domain)

                        if domain_match:
                            threshold.write({'is_applied': True})  # ✅ mark threshold as applied
                            threshold_name = threshold.threshold_name or 'Unnamed Threshold'
                            line.write({
                                'applied_trigger_line_id': rule_rec.id,
                                'applied_threshold_name': threshold_name,
                                'is_trigger_applied': True,
                                'trigger_row_color': triggermain.row_color,
                            })
                            _logger.info("✅ Trigger applied (rules_by_domain) on line %s | Threshold: %s",
                                         line.id, threshold_name)
                            rule_applied = True
                            break
                        else:
                            _logger.info("❌ Domain not satisfied for line %s → skipping", line.id)
                    elif threshold.condition_type_forecast == 'rules':
                        _logger.info("🔍 Condition type: rules for %s", threshold.threshold_name)
                        previous_result = None
                        current_operator = None
                        combined_result = None
                        rule_result_map = {}

                        for rule in threshold.threshold_line_ids:
                            field_1_val = getattr(line, rule.field_1.name, 0) if rule.field_1 else 0
                            field_2_val = getattr(line, rule.field_2.name, 0) if rule.field_2 else 0
                            result = False

                            if rule_applied:
                                break  # stop if already applied

                            if rule.change_type and field_1_val is not None and field_2_val is not None:
                                # Apply percentage on field_1
                                if rule.change_type == 'increase':
                                    # True if actual value meets or exceeds the target
                                    result = field_2_val >= field_1_val * (1 + rule.percentage)
                                elif rule.change_type == 'decrease':
                                    # True if actual value is below or equal to the target
                                    result = field_2_val <= field_1_val * (1 - rule.percentage)

                            if rule.trigger_value and rule.operator:
                                if rule.operator == '<':
                                    result = field_1_val < rule.trigger_value
                                elif rule.operator == '<=':
                                    result = field_1_val <= rule.trigger_value
                                elif rule.operator == '>':
                                    result = field_1_val > rule.trigger_value
                                elif rule.operator == '>=':
                                    result = field_1_val >= rule.trigger_value

                            rule_result_map[rule.id] = result
                            _logger.info("Rule %s result: %s", rule.id, result)

                            # --- Combine results ---
                            if previous_result is None:
                                combined_result = result
                            else:
                                if current_operator == 'AND':
                                    combined_result = previous_result and result
                                elif current_operator == 'OR':
                                    combined_result = previous_result or result

                            previous_result = combined_result
                            current_operator = rule.logical

                        # ✅ Apply if overall result is true
                        if combined_result:
                            threshold.write({'is_applied': True})  # ✅ mark threshold as applied
                            # Find which rule triggered
                            first_true_rule = next((r for r, res in rule_result_map.items() if res), None)
                            if first_true_rule:
                                rule_rec = self.env['trigger.threshold.line'].browse(first_true_rule)
                                threshold_name = rule_rec.threshold_id.threshold_name or 'Unnamed Threshold'

                                line.write({
                                    'applied_trigger_line_id': rule_rec.id,
                                    'applied_threshold_name': threshold_name,
                                    'is_trigger_applied': True,
                                    'trigger_row_color': triggermain.row_color,
                                })
                                rule_applied = True

                                _logger.info(
                                    "✅ Trigger applied on line %s | Threshold: %s | Rule ID: %s",
                                    line.id, threshold_name, rule_rec.id
                                )
            if rule_applied:
                triggered_lines |= line

        return triggered_lines

    def action_show_list_view(self):
        """
              Authour: nidhi@setconsulting
              Date: 9th Oct 2025
              Task: [12538] Forecast Report Generation On Screen
              Purpose: This method will be executed when the process is Forecast-->Export Forecast Report.
                   This will work only when type is reordering.
                   Generate on-screen tree view report for forecast with proper rates and total units.
        """
        self.ensure_one()

        start_time = time.time()
        _logger.info("Start action_show_list_view at %.3f", start_time)
        today_date = fields.Date.today()

        ForecastLine = self.env['forecast.report.line']
        model_fields = ForecastLine.fields_get().keys()
        HistoryModel = self.env['forecast.report.history']
        all_margins = self.env['forecast.report.amz.margin'].search([])

        # 2. Initialize warehouses & periods
        init_start = time.time()
        self._init_lists()
        selected_periods = [str(x.days) for x in self.periods]
        all_periods = [str(x.days) for x in self.env['forecast.days.config'].search([])]
        _logger.info("Init warehouses/periods time: %.3f seconds", time.time() - init_start)

        # 3. Fetch raw forecast data
        query_start = time.time()
        query = super(ExportForecastWizard, self)._get_request()
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        _logger.info("SQL fetch time: %.3f seconds", time.time() - query_start)

        default_delay = self.env['product.supplierinfo']._get_default_delay()
        product_statuses = dict(self.env['product.product']._fields['product_status'].selection)
        today = fields.Date.today()

        # 3️⃣ Search for existing identical history
        existing_history = None
        candidate_histories = HistoryModel.search([
            ('history_forecast_type', '=', self.type),
            ('history_region', '=', self.region),
            ('history_is_exclude_oos_days', '=', self.is_exclude_oos_days),
            ('history_use_constant_lead_time', '=', self.use_constant_lead_time),
            ('history_delivery_lead_time', '=', self.delivery_lead_time),
            ('run_date', '>=', today),  # <-- only today
            ('run_date', '<', today + timedelta(days=1)),  # <-- up to next day
        ], order='run_date desc')

        for candidate_history in candidate_histories:
            same_filters = self._compare_filter_sets(candidate_history.history_filters_ids, self.filters)
            if set(candidate_history.history_periods_ids.ids) == set(self.periods.ids) and \
                set(candidate_history.history_product_status_filter_ids.ids) == set(self.product_status_filter.ids) and \
                set(candidate_history.history_amazon_product_status_filter_ids.ids) == set(
                self.amazon_product_status_filter.ids) and \
                same_filters:
                existing_history = candidate_history
                break

        if existing_history:
            _logger.info("Identical history found: %s", existing_history.name)
            current_datetime = fields.Datetime.now()
            existing_history.write({'run_date': current_datetime,
                                    'name': f'Forecast History {current_datetime} Updated'})
            triggered_lines_in_history = self.env['forecast.report.line'].search([
                ('history_id', '=', existing_history.id),
                ('is_trigger_applied', '=', True)  # <-- only lines that were triggered
            ])
            return {
                'name': _('Forecast On-screen report ({}) Updated'.format(current_datetime)),
                'type': 'ir.actions.act_window',
                'res_model': 'forecast.report.line',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', triggered_lines_in_history.ids)],
                'target': 'current',
                'context': {'default_history_id': existing_history.id},
            }

        # 4. Create a new Forecast History (only if no identical exists)
        history = HistoryModel.create({
            'name': f'Forecast History {today_date.strftime("%Y-%m-%d")}',
            'run_date': today_date,
            'history_forecast_type': self.type,
            'history_region': self.region,
            'history_periods_ids': [(6, 0, self.periods.ids)],
            'history_is_exclude_oos_days': self.is_exclude_oos_days,
            'history_product_status_filter_ids': [(6, 0, self.product_status_filter.ids)],
            'history_amazon_product_status_filter_ids': [(6, 0, self.amazon_product_status_filter.ids)],
            'history_use_constant_lead_time': self.use_constant_lead_time,
            'history_delivery_lead_time': self.delivery_lead_time,
            'history_filters_ids': [
                (0, 0, {
                    'name': f.name,
                    'type': f.type,
                    'is_used': f.is_used,
                    'from_filter': f.from_filter,
                    'to_filter': f.to_filter,
                    'periods': [(6, 0, f.periods.ids)],
                })
                for f in self.filters
            ],
            'history_purchase_order_based_on_doi_id': self.purchase_order_based_on_doi_id.id if self.purchase_order_based_on_doi_id else False,
        })
        _logger.info("History Created: %s", history.name)
        process_start = time.time()
        grouped_data = {}

        for rec in result:
            if rec['wh'] and rec['wh'] not in self.wh_filters['warehouses'] and rec['wh'] not in self.wh_filters[
                'amz_warehouses']:
                continue

            product = grouped_data.get(rec['id'], {})

            # Basic product info
            product.update({
                'id': rec['id'],
                'product_tmpl_id': rec['product_tmpl_id'],
                'name': rec['name'],
                'sku': rec['sku'],
                'product_status': product_statuses.get(rec['product_status']),
                'total_in_transit': product.get('total_in_transit', 0) + rec['total_in_transit'],
                'total_air_in_transit': product.get('total_air_in_transit', 0) + rec['total_air_in_transit'],
                'total_on_order': product.get('total_on_order', 0) + rec['total_on_order'],
                'total_qty_on_hand': product.get('total_qty_on_hand', 0) + rec['total_qty_on_hand'],
                'total_inbound': product.get('total_inbound', 0) + rec['total_inbound'],
                'minimum_daily_sales_rate': rec['minimum_daily_sales_rate'],
                'delay': rec['delay'],
                'price': rec['price'],
                'case_qty': int(rec['case_qty'] or 0),
                'has_a_multiple_case_qty': rec['has_a_multiple_case_qty'],
                'has_a_removal_date': rec['has_a_removal_date'],
                'has_product_update_details': rec['has_product_update_details'],
                'min_qty': rec['min_qty'],
                'supplier': rec['supplier'],
                'sold_in_amazon': rec['sold_in_amazon'],
                'is_large_product': rec['is_large_product'],
                'is_used_in_boms': rec['is_used_in_boms'],
            })

            # Safe days_from_sale handling
            existing_days = product.get('days_from_sale')
            new_days = rec['days_from_sale']
            if new_days != 9999:
                if existing_days is None:
                    product['days_from_sale'] = new_days
                else:
                    product['days_from_sale'] = min(existing_days, new_days)

            # Compute sales per period
            for days in all_periods:
                total_key = f'total_sales_{days}'
                total_key_amz = f'total_sales_amz_{days}'
                bom_key = f'bom_{total_key}'

                product[total_key] = product.get(total_key, 0) + rec.get(total_key, 0)
                product[total_key_amz] = product.get(total_key_amz, 0) + rec.get(total_key_amz, 0)
                product[bom_key] = product.get(bom_key, 0) + rec.get(bom_key, 0)

                # Sales per warehouse
                if rec['wh'] and rec['wh'] not in self.wh_filters['amz_warehouses']:
                    product[f'total_sales_{rec["wh"]}{days}'] = rec.get(total_key, 0)
                elif rec['wh']:
                    fba_key = f'total_sales_fba_{days}'
                    product[fba_key] = product.get(fba_key, 0) + rec.get(total_key, 0)

            # Compute total units per warehouse
            if rec['wh']:
                total_wh_key = f'total_units_{rec["wh"]}'
                product[total_wh_key] = (
                    product.get(total_wh_key, 0) + rec['total_in_transit'] + rec['total_on_order'] +
                    rec['total_qty_on_hand'] + rec['total_inbound']
                )
                inbound_key = f'inbound_units_{rec["wh"]}'
                product[inbound_key] = product.get(inbound_key, 0) + rec['total_qty_on_hand_inb']

            # Compute overall totals
            if rec['wh'] in self.wh_list:
                product['total_units_total'] = (
                    product.get('total_units_total', 0) + rec['total_in_transit'] +
                    rec['total_on_order'] + rec['total_qty_on_hand']
                )
                product['inbound_units_total'] = (
                    product.get('inbound_units_total', 0) + rec['total_qty_on_hand_inb']
                )

            # OOS values per period
            product['oos_warehouse'] = {x: rec.get(f'oos_warehouse_{x}', 0) for x in all_periods}
            product['oos_amazon'] = {x: rec.get(f'oos_amazon_{x}', 0) for x in all_periods}
            product['oos_total'] = {x: rec.get(f'oos_total_{x}', 0) for x in all_periods}

            if not product['sold_in_amazon']:
                product['oos_amazon'] = {x: '-' for x in all_periods}
                product['oos_total'] = product['oos_warehouse']

            grouped_data[rec['id']] = product
        _logger.info("Processing records time: %.3f seconds", time.time() - process_start)

        rates_start = time.time()
        forecast_lines_vals = []
        # 4. Compute rates and create Forecast Lines
        for product_id, product in grouped_data.items():
            delay = self.delivery_lead_time if self.use_constant_lead_time else product.get('delay') or default_delay
            minimum_daily_rate = product.get('minimum_daily_sales_rate')

            # Compute total units
            total_units = getattr(self, f'get_total_units_{self.type}')(product)

            rates = {
                'DOI': {},
                'DUR': {},
                'quantity_to_buy': {},
                'daily_rate': {},
                'daily_rate_amz': {},
                'bom_daily_rate': {},
                'total_daily_rate': {},
                'total_units': total_units,
            }

            for days in all_periods:
                period_exc_oos = int(days)
                oos_value = product['oos_amazon' if self.type == 'inbound' else 'oos_total'].get(days, 0)
                if self.is_exclude_oos_days and oos_value and oos_value != '-':
                    period_exc_oos -= oos_value

                if period_exc_oos == 0:
                    daily_rate = daily_rate_amz = daily_rate_bom = daily_rate_total = 0
                else:
                    daily_rate = product.get(f'total_sales_{days}', 0) / period_exc_oos
                    daily_rate_amz = product.get(f'total_sales_amz_{days}', 0) / period_exc_oos
                    daily_rate_bom = product.get(f'bom_total_sales_{days}', 0) / period_exc_oos
                    daily_rate_total = (product.get(f'total_sales_{days}', 0) + product.get(f'bom_total_sales_{days}',
                                                                                            0)) / period_exc_oos

                # Respect minimum daily rate
                if minimum_daily_rate:
                    if self.type in ['reordering', 'inbound', 'shipping']:
                        daily_rate_total = max(daily_rate_total, minimum_daily_rate)
                        _logger.info("minimum_daily_rate execution")
                    else:
                        daily_rate = max(daily_rate, minimum_daily_rate)
                        daily_rate_total = daily_rate

                rates['daily_rate'][days] = daily_rate
                rates['daily_rate_amz'][days] = daily_rate_amz
                rates['bom_daily_rate'][days] = daily_rate_bom
                rates['total_daily_rate'][days] = daily_rate_total
                rates['DOI'][days] = self._calc_doi(daily_rate_total, total_units)
                rates['DUR'][days] = rates['DOI'][days] - int(delay)
                rates['quantity_to_buy'][days] = max(-1 * rates['DUR'][days] * daily_rate_total, 0)

            # Create ORM Forecast Line
            prod_obj = self.env['product.product'].browse(product_id)
            product['product_category_id'] = prod_obj.categ_id.id
            supplier_name = product.get('supplier')
            supplier = self.env['res.partner'].search([('name', '=', supplier_name)], limit=1)

            # Get all price.calculator lines for this product
            lines_for_product = self.env['price.calculator.line'].search([]).filtered(
                lambda l: l.product_id.id == prod_obj.id
            )
            if lines_for_product:
                # Sort by qty ascending, take the first (lowest qty)
                min_qty_line = lines_for_product.sorted(key=lambda l: l.qty)[0]
                margin_value = min_qty_line.margin
            else:
                margin_value = 0.0
                _logger.info("No price.calculator.line found for product %s", prod_obj.display_name)

            # Check filters before adding to report (same as export_data)
            if self.type == 'reordering':
                # If product doesn’t satisfy filters, skip it
                if not all(x.check_filter(rates, product.get('is_large_product')) for x in self.filters):
                    continue
            vals = {
                'history_id': history.id,  # set your forecast history id variable
                'product_id': product.get('id'),
                'name': product.get('name'),
                'sku': product.get('sku'),
                'product_status': product.get('product_status'),
                'supplier_id': supplier.id if supplier else False,
                'shipments_in_transit': product.get('total_in_transit'),
                'fba_inbound': product.get('total_inbound'),
                'on_order': product.get('total_on_order'),
                'on_hand': product.get('total_qty_on_hand'),
                'overall_total_units': rates.get('total_units', 0.0),
                'total_units': product.get('total_units_total', 0),
                'case_qty': product.get('case_qty'),
                'has_product_update_details': product.get('has_product_update_details'),
                'unit_cost': product.get('price'),
                'product_category_id': product['product_category_id'],
                'warning_msg': prod_obj.purchase_line_warn_msg,
                'margin': (
                    all_margins.filtered_domain([('amz_margin_product_id', '=', prod_obj.id)])[:1].amz_margin * 100
                    if all_margins.filtered_domain([('amz_margin_product_id', '=', prod_obj.id)])[:1]
                    else 0.0
                ),
                'b2b': margin_value
            }
            for period in all_periods:
                field_name = f'total_sales_{period}'
                if field_name in model_fields:
                    vals[field_name] = product.get(field_name, 0.0)

                for prefix, key in [
                    ('total_daily_rate', 'total_daily_rate'),
                    ('doi', 'DOI'),
                    ('quantity_to_buy', 'quantity_to_buy'),
                ]:
                    field_name = f"{prefix}_{period}"
                    if field_name in model_fields:
                        # vals[field_name] = rates[key].get(period, 0.0) if period in selected_periods else 0.0
                        value = rates[key].get(period, 0.0) if period in selected_periods else 0.0
                        if key in ['doi', 'quantity_to_buy']:
                            value = int(round(value))
                        vals[field_name] = value

            if self.purchase_order_based_on_doi_id:
                selected_days = str(self.purchase_order_based_on_doi_id.days)
                _logger.info("Selected DOI days for QTB calc: %s", selected_days)

                delay = self.delivery_lead_time if self.use_constant_lead_time else self.env[
                    'product.supplierinfo']._get_default_delay()
                case_qty = max(product['case_qty'], 1)

                # ✅ Reinitialize for each product
                total_fba_units = 0
                cross_wh_total_to_buy = 0
                wh_to_buy_data = {}

                fba_sales_key = f'total_sales_fba_{selected_days}'

                # Sum Amazon units
                for wh in self.wh_filters['amz_warehouses'].values():
                    total_fba_units += product.get(f'total_units_%s' % wh.name, 0)

                wh_days = int(selected_days)
                if self.is_exclude_oos_days:
                    oos_wh_value = product['oos_warehouse'].get(selected_days, 0)
                    wh_days -= int(oos_wh_value) if isinstance(oos_wh_value, (int, float)) else 0
                    # wh_days -= product['oos_warehouse'].get(selected_days, 0) or 0

                fba_days = int(selected_days)
                if self.is_exclude_oos_days:
                    oos_amz_value = product['oos_amazon'].get(selected_days, 0)
                    fba_days -= int(oos_amz_value) if isinstance(oos_amz_value, (int, float)) else 0
                    # fba_days -= product['oos_amazon'].get(selected_days, 0) or 0

                # Compute per-warehouse totals
                for wh in [x for x in self.wh_list.values() if x.rebalancing_perc]:
                    wh_key = f'total_units_{wh.name}'
                    sales_wh_key = f'total_sales_{wh.name}{selected_days}'

                    total_units = product.get(wh_key, 0) + total_fba_units * wh.rebalancing_perc / 100
                    daily_rate = wh_days and (product.get(sales_wh_key, 0) / wh_days) or 0
                    if fba_days:
                        daily_rate += (product.get(fba_sales_key, 0) / fba_days * wh.rebalancing_perc / 100)

                    total_value = daily_rate and float_round(
                        -(-delay + total_units / daily_rate) * daily_rate / case_qty,
                        0
                    ) * case_qty or 0

                    if total_value > 0:
                        cross_wh_total_to_buy += total_value

                    wh_to_buy_data[wh.name] = max(0, total_value)

                # ✅ Distribute across warehouses
                for key, value in wh_to_buy_data.items():
                    if cross_wh_total_to_buy > 0:
                        qtb = rates['quantity_to_buy'][selected_days] / cross_wh_total_to_buy * value
                        wh_to_buy_data[key] = float_round(qtb / case_qty, 0) * case_qty
                    else:
                        wh_to_buy_data[key] = 0

                qtb_data_warehouse = {wh: float_round(val or 0, 2) for wh, val in wh_to_buy_data.items()}
                vals['qtb_data_warehouse'] = qtb_data_warehouse

                _logger.info("✅ QTB distributed for %s: %s", product.get('sku'), qtb_data_warehouse)

            forecast_lines_vals.append(vals)
        _logger.info("Computing rates and preparing vals time: %.3f seconds", time.time() - rates_start)

        create_start = time.time()
        forecast_lines = ForecastLine.create(forecast_lines_vals)
        _logger.info("ForecastLine creation time: %.3f seconds", time.time() - create_start)
        triggered_lines = self._apply_triggers_to_lines(forecast_lines)
        if not triggered_lines:
            # Fallback: get lines that have is_trigger_applied=True (maybe from past run)
            triggered_lines = forecast_lines.filtered(lambda l: l.is_trigger_applied)
            if not triggered_lines:
                _logger.warning("⚠ No rules applied to any forecast line — showing all lines temporarily.")
                triggered_lines = forecast_lines  # fallback for debugging
            else:
                # Update history lines to only include triggered lines
                triggered_lines.write({'history_id': history.id})

        # 5. Return tree view
        report_date = fields.Date.context_today(self)

        return {
            'name': _('Forecast On-screen report ({})'.format(report_date.strftime('%Y-%m-%d'))),
            'type': 'ir.actions.act_window',
            'res_model': 'forecast.report.line',
            'view_mode': 'tree',
            'domain': [('id', 'in', triggered_lines.ids)],
            'target': 'current',
            'context': {
                'default_history_id': history.id,  # link context to this history
                'default_line_purchase_order_doi_days': int(
                    self.purchase_order_based_on_doi_id.days) if self.purchase_order_based_on_doi_id else False,
            },
        }

    def _compare_filter_sets(self, history_filters, current_filters):
        """Compare history filters with current wizard filters."""
        if len(history_filters) != len(current_filters):
            return False

        def key(f):
            return (f.type, f.is_used, f.from_filter or '', f.to_filter or '', tuple(sorted(f.periods.ids)))

        return sorted(map(key, history_filters)) == sorted(map(key, current_filters))

