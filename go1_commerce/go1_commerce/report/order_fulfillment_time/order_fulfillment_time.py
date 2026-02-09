# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary

def get_columns():
	return [
		_("Order") + ":Link/Order:150",
		_("Customer") + ":Data:180",
		_("Order Date") + ":Date:120",
		_("Status") + ":Data:100",
		_("Shipping Status") + ":Data:120",
		_("Days Since Order") + ":Int:120",
		_("Total Amount") + ":Currency:120",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	query = (
		frappe.qb.from_(OrderDT)
		.select(
			OrderDT.name,
			OrderDT.customer_name,
			OrderDT.order_date,
			OrderDT.status,
			OrderDT.shipping_status,
			OrderDT.total_amount,
			OrderDT.creation,
		)
		.where(OrderDT.docstatus == 1)
		.orderby(OrderDT.order_date, order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	today = frappe.utils.getdate()
	result = []
	for r in raw:
		order_date = frappe.utils.getdate(r.order_date) if r.order_date else today
		days = (today - order_date).days
		result.append([
			r.name, r.customer_name, r.order_date,
			r.status, r.shipping_status or "N/A",
			days, float(r.total_amount or 0)
		])
	return result

def get_chart_data(data):
	if not data:
		return None

	buckets = {"0-1 day": 0, "2-3 days": 0, "4-7 days": 0, "8-14 days": 0, "15-30 days": 0, "30+ days": 0}
	for row in data:
		days = row[5]
		if days <= 1:
			buckets["0-1 day"] += 1
		elif days <= 3:
			buckets["2-3 days"] += 1
		elif days <= 7:
			buckets["4-7 days"] += 1
		elif days <= 14:
			buckets["8-14 days"] += 1
		elif days <= 30:
			buckets["15-30 days"] += 1
		else:
			buckets["30+ days"] += 1

	return {
		"data": {
			"labels": list(buckets.keys()),
			"datasets": [{"name": _("Orders"), "values": list(buckets.values())}]
		},
		"type": "bar",
		"colors": ["#4E79A7"]
	}

def get_summary(data):
	if not data:
		return []
	days_list = [row[5] for row in data]
	avg_days = round(sum(days_list) / max(len(days_list), 1), 1)
	pending = sum(1 for row in data if row[3] in ("Placed", "Processing"))
	return [
		{"value": avg_days, "label": _("Avg Days Since Order"), "datatype": "Float"},
		{"value": len(data), "label": _("Total Orders"), "datatype": "Int"},
		{"value": pending, "label": _("Pending Fulfillment"), "datatype": "Int"},
	]
