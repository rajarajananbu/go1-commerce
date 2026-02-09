# Copyright (c) 2023, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import IfNull, Count, Concat

def execute(filters=None):
	columns, data = get_columns(), get_datas(filters)
	return columns, data

def get_columns():
	return [
		_("Customer ID") + ":Link/Customers:150",
		_("First Name") + ":Data:150",
		_("Last Name") + ":Data:100",
		_("Email") + ":Data:200",
		_("Phone") + ":Phone:150",
		_("Created") + ":Date:120",
		_("Updated") + ":Date:120",
		_("Orders Count") + ":Int:100",
		_("Last Ordered Id") + ":Link/Order:150",
		_("Store Name") + ":Data:150",
		_("Address") + ":Data:300",
		_("City") + ":Data:120",
		_("State") + ":Data:120",
		_("Country") + ":Data:120",
		_("Pincode") + ":Data:100",
		_("Customer Type") + ":Data:150",
	]

def get_datas(filters):
	CustomerDT = DocType("Customers")
	OrderDT = DocType("Order")

	query = (
		frappe.qb.from_(CustomerDT)
		.left_join(OrderDT).on(
			(OrderDT.customer == CustomerDT.name) &
			(OrderDT.docstatus == 1)
		)
		.select(
			CustomerDT.name,
			CustomerDT.first_name,
			CustomerDT.last_name,
			CustomerDT.email,
			CustomerDT.phone,
			CustomerDT.creation,
			CustomerDT.modified,
			Count(OrderDT.name).as_("orders_count"),
			frappe.qb.terms.ValueWrapper("").as_("last_ordered_id"),
			CustomerDT.store_name,
			CustomerDT.address,
			CustomerDT.city,
			CustomerDT.state,
			CustomerDT.country,
			CustomerDT.zipcode,
			CustomerDT.business_type,
		)
		.groupby(CustomerDT.name)
		.orderby(CustomerDT.creation, order=frappe.qb.desc)
	)

	if filters and filters.get('from_date'):
		query = query.where(CustomerDT.creation >= filters.get('from_date'))
	if filters and filters.get('to_date'):
		query = query.where(CustomerDT.creation <= filters.get('to_date'))

	result = query.run(as_dict=True)

	for row in result:
		last_order = frappe.db.get_value(
			"Order",
			{"customer": row.name, "docstatus": 1},
			"name",
			order_by="creation desc"
		)
		row["last_ordered_id"] = last_order or ""

	return [[
		r.name, r.first_name, r.last_name, r.email, r.phone,
		r.creation, r.modified, r.orders_count, r.last_ordered_id,
		r.store_name, r.address, r.city, r.state, r.country,
		r.zipcode, r.business_type
	] for r in result]
