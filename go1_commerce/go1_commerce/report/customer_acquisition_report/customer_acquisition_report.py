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
	return columns, data, None, chart

def get_columns():
	return [
		_("Month") + ":Data:120",
		_("New Customers") + ":Int:120",
		_("Cumulative Customers") + ":Int:150",
	]

def get_data(filters):
	CustomerDT = DocType("Customers")
	year = int(filters.get("year")) if filters.get("year") else frappe.utils.getdate().year
	month_list = ["January", "February", "March", "April", "May", "June",
				  "July", "August", "September", "October", "November", "December"]

	query = (
		frappe.qb.from_(CustomerDT)
		.select(
			Function("MONTHNAME", CustomerDT.creation).as_("month"),
			Function("MONTH", CustomerDT.creation).as_("month_num"),
			Count("*").as_("new_customers"),
		)
		.where(Function("YEAR", CustomerDT.creation) == year)
		.where(CustomerDT.customer_status == "Approved")
		.groupby(Function("MONTH", CustomerDT.creation))
		.orderby(Function("MONTH", CustomerDT.creation))
	)
	if filters.get("from_date"):
		query = query.where(CustomerDT.creation >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(CustomerDT.creation <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	month_data = {r.month: int(r.new_customers or 0) for r in raw}

	result = []
	cumulative = 0
	for m in month_list:
		new = month_data.get(m, 0)
		cumulative += new
		result.append([m, new, cumulative])
	return result

def get_chart_data(data):
	if not data:
		return None
	labels = [row[0] for row in data]
	new_customers = [row[1] for row in data]
	cumulative = [row[2] for row in data]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("New Customers"), "type": "bar", "values": new_customers},
				{"name": _("Cumulative"), "type": "line", "values": cumulative},
			]
		},
		"type": "axis-mixed",
		"colors": ["#76B7B2", "#4E79A7"]
	}
