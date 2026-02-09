# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	return [
		_("Product") + ":Link/Product:150",
		_("Product Name") + ":Data:200",
		_("Total Sold") + ":Int:100",
		_("Total Returns") + ":Int:100",
		_("Return Rate") + ":Percent:100",
		_("Return Reasons") + ":Data:250",
	]

def get_data(filters):
	Product = DocType("Product")
	OrderItem = DocType("Order Item")
	OrderDT = DocType("Order")
	ReturnRequest = DocType("Return Request")
	ReturnItem = DocType("Return Request Item")

	sold_query = (
		frappe.qb.from_(OrderItem)
		.inner_join(OrderDT).on(OrderDT.name == OrderItem.parent)
		.select(
			OrderItem.item.as_("product"),
			Sum(OrderItem.quantity).as_("total_sold"),
		)
		.where(OrderDT.docstatus == 1)
		.where(OrderDT.payment_status == "Paid")
		.groupby(OrderItem.item)
	)
	if filters.get("from_date"):
		sold_query = sold_query.where(OrderDT.order_date >= filters.get("from_date"))
	if filters.get("to_date"):
		sold_query = sold_query.where(OrderDT.order_date <= filters.get("to_date"))
	sold_data = {r.product: int(r.total_sold or 0) for r in sold_query.run(as_dict=True)}

	return_query = (
		frappe.qb.from_(ReturnItem)
		.inner_join(ReturnRequest).on(ReturnRequest.name == ReturnItem.parent)
		.select(
			ReturnItem.item.as_("product"),
			Count("*").as_("return_count"),
		)
		.where(ReturnRequest.docstatus == 1)
		.groupby(ReturnItem.item)
	)
	if filters.get("from_date"):
		return_query = return_query.where(ReturnRequest.creation >= filters.get("from_date"))
	if filters.get("to_date"):
		return_query = return_query.where(ReturnRequest.creation <= filters.get("to_date"))

	try:
		return_data = {r.product: int(r.return_count or 0) for r in return_query.run(as_dict=True)}
	except Exception:
		return_data = {}

	reason_query = (
		frappe.qb.from_(ReturnItem)
		.inner_join(ReturnRequest).on(ReturnRequest.name == ReturnItem.parent)
		.select(
			ReturnItem.item.as_("product"),
			ReturnRequest.return_reason,
		)
		.where(ReturnRequest.docstatus == 1)
	)
	try:
		reason_raw = reason_query.run(as_dict=True)
	except Exception:
		reason_raw = []

	reasons_map = {}
	for r in reason_raw:
		if r.product not in reasons_map:
			reasons_map[r.product] = set()
		if r.return_reason:
			reasons_map[r.product].add(r.return_reason)

	all_products = set(list(sold_data.keys()) + list(return_data.keys()))
	product_names = {}
	if all_products:
		for p in frappe.get_all("Product", filters={"name": ["in", list(all_products)]}, fields=["name", "item"]):
			product_names[p.name] = p.item

	result = []
	for product in all_products:
		sold = sold_data.get(product, 0)
		returns = return_data.get(product, 0)
		if returns == 0:
			continue
		rate = round((returns / max(sold, 1)) * 100, 2)
		reasons = ", ".join(reasons_map.get(product, []))
		result.append([
			product, product_names.get(product, product),
			sold, returns, rate, reasons
		])

	result.sort(key=lambda x: x[4], reverse=True)
	return result

def get_chart_data(data):
	if not data:
		return None
	labels = [row[1] or row[0] for row in data[:15]]
	return_rates = [float(row[4] or 0) for row in data[:15]]
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Return Rate %"), "values": return_rates}]
		},
		"type": "bar",
		"colors": ["#E15759"]
	}
