# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count, Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Return Request") + ":Link/Return Request:150",
		_("Order") + ":Link/Order:150",
		_("Customer") + ":Data:180",
		_("Return Date") + ":Date:120",
		_("Reason") + ":Data:200",
		_("Status") + ":Data:120",
		_("Refund Amount") + ":Currency:130",
	]

def get_data(filters):
	ReturnRequest = DocType("Return Request")

	query = (
		frappe.qb.from_(ReturnRequest)
		.select(
			ReturnRequest.name,
			ReturnRequest.order,
			ReturnRequest.customer_name,
			ReturnRequest.creation,
			ReturnRequest.return_reason,
			ReturnRequest.status,
			ReturnRequest.total_amount,
		)
		.where(ReturnRequest.docstatus == 1)
		.orderby(ReturnRequest.creation, order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(ReturnRequest.creation >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(ReturnRequest.creation <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	return [
		[r.name, r.order, r.customer_name, r.creation,
		 r.return_reason or "N/A", r.status, float(r.total_amount or 0)]
		for r in raw
	]

def get_chart_data(data):
	if not data:
		return None

	reason_totals = {}
	for row in data:
		reason = row[4]
		reason_totals[reason] = reason_totals.get(reason, 0) + 1

	sorted_reasons = sorted(reason_totals.items(), key=lambda x: x[1], reverse=True)
	labels = [r[0] for r in sorted_reasons[:10]]
	values = [r[1] for r in sorted_reasons[:10]]

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Returns"), "values": values}]
		},
		"type": "pie",
		"colors": ["#E15759", "#F28E2B", "#76B7B2", "#EDC948", "#B07AA1", "#FF9DA7", "#4E79A7", "#59A14F"]
	}
