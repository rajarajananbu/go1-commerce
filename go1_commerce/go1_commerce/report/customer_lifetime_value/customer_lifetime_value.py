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
		_("Customer") + ":Link/Customers:150",
		_("Customer Name") + ":Data:200",
		_("Email") + ":Data:200",
		_("First Order") + ":Date:120",
		_("Last Order") + ":Date:120",
		_("Total Orders") + ":Int:100",
		_("Total Spent") + ":Currency:150",
		_("Avg Order Value") + ":Currency:130",
		_("Customer Since (Days)") + ":Int:130",
	]

def get_data(filters):
	OrderDT = DocType("Order")
	CustomerDT = DocType("Customers")
	min_orders = int(filters.get("min_orders") or 1)

	query = (
		frappe.qb.from_(OrderDT)
		.inner_join(CustomerDT).on(OrderDT.customer == CustomerDT.name)
		.select(
			CustomerDT.name.as_("customer_id"),
			CustomerDT.full_name,
			CustomerDT.email,
			Function("MIN", OrderDT.order_date).as_("first_order"),
			Function("MAX", OrderDT.order_date).as_("last_order"),
			Count("*").as_("total_orders"),
			Sum(OrderDT.total_amount).as_("total_spent"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.groupby(CustomerDT.name)
		.having(Count("*") >= min_orders)
		.orderby(Sum(OrderDT.total_amount), order=frappe.qb.desc)
	)
	if filters.get("from_date"):
		query = query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(OrderDT.order_date <= filters.get("to_date"))

	raw = query.run(as_dict=True)
	today = frappe.utils.getdate()
	result = []
	for r in raw:
		orders = int(r.total_orders or 0)
		spent = float(r.total_spent or 0)
		avg = round(spent / max(orders, 1), 2)
		first = frappe.utils.getdate(r.first_order) if r.first_order else today
		days_since = (today - first).days
		result.append([
			r.customer_id, r.full_name, r.email,
			r.first_order, r.last_order,
			orders, spent, avg, days_since
		])
	return result

def get_chart_data(data):
	if not data:
		return None
	labels = [row[1] or row[0] for row in data[:20]]
	values = [float(row[6] or 0) for row in data[:20]]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Lifetime Value"), "values": values}]
		},
		"type": "bar",
		"colors": ["#59A14F"],
		"barOptions": {"spaceRatio": 0.3}
	}
