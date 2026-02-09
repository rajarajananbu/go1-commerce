# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum, Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary

def get_columns():
	return [
		_("Customer") + ":Link/Customers:150",
		_("Customer Name") + ":Data:200",
		_("Email") + ":Data:200",
		_("Last Order Date") + ":Date:120",
		_("Days Inactive") + ":Int:100",
		_("Total Orders") + ":Int:100",
		_("Total Spent") + ":Currency:130",
		_("Risk Level") + ":Data:100",
	]

def get_data(filters):
	inactive_days = int(filters.get("inactive_days") or 90)
	OrderDT = DocType("Order")
	CustomerDT = DocType("Customers")

	query = (
		frappe.qb.from_(CustomerDT)
		.inner_join(OrderDT).on(OrderDT.customer == CustomerDT.name)
		.select(
			CustomerDT.name.as_("customer_id"),
			CustomerDT.full_name,
			CustomerDT.email,
			Function("MAX", OrderDT.order_date).as_("last_order"),
			Count("*").as_("total_orders"),
			Sum(OrderDT.total_amount).as_("total_spent"),
		)
		.where(OrderDT.docstatus == 1)
		.where(CustomerDT.customer_status == "Approved")
		.groupby(CustomerDT.name)
		.orderby(Function("MAX", OrderDT.order_date))
	)
	raw = query.run(as_dict=True)
	today = frappe.utils.getdate()

	result = []
	for r in raw:
		last_date = frappe.utils.getdate(r.last_order) if r.last_order else today
		days = (today - last_date).days
		if days < inactive_days:
			continue

		if days >= inactive_days * 3:
			risk = "Lost"
		elif days >= inactive_days * 2:
			risk = "High"
		elif days >= inactive_days:
			risk = "Medium"
		else:
			risk = "Low"

		result.append([
			r.customer_id, r.full_name, r.email,
			r.last_order, days,
			int(r.total_orders or 0), float(r.total_spent or 0),
			risk
		])
	return result

def get_chart_data(data):
	if not data:
		return None

	risk_counts = {}
	for row in data:
		risk = row[7]
		risk_counts[risk] = risk_counts.get(risk, 0) + 1

	labels = list(risk_counts.keys())
	values = list(risk_counts.values())

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Customers"), "values": values}]
		},
		"type": "pie",
		"colors": ["#F28E2B", "#E15759", "#86888A"]
	}

def get_summary(data):
	if not data:
		return []
	total = len(data)
	total_revenue_at_risk = sum(float(row[6] or 0) for row in data)
	return [
		{"value": total, "label": _("Churned Customers"), "datatype": "Int"},
		{"value": total_revenue_at_risk, "label": _("Revenue at Risk"), "datatype": "Currency"},
	]
