# Copyright (c) 2023, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Function

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		_("Cash Collection Date") + ":Date:150",
		_("Cash Approval Date") + ":Date:150",
		_("Customer") + ":Link/Customers:120",
		_("Customer Name") + ":Data:150",
		_("Against") + ":Data:120",
		_("Against Reference") + ":Data:150",
		_("Order ID") + ":Link/Order:150",
		_("Amount") + ":Currency:120",
	]

def get_data(filters):
	PaymentEntry = DocType('Payment Entry')
	PaymentReference = DocType('Payment Reference')
	CustomerDT = DocType('Customers')

	query = (
		frappe.qb.from_(PaymentEntry)
		.inner_join(PaymentReference).on(PaymentEntry.name == PaymentReference.parent)
		.inner_join(CustomerDT).on(CustomerDT.name == PaymentEntry.party)
		.select(
			PaymentEntry.modified.as_('cash_approval_date'),
			PaymentEntry.modified.as_('cash_approval_date_2'),
			PaymentEntry.party.as_('customer'),
			CustomerDT.first_name.as_('customer_name'),
			PaymentReference.reference_doctype.as_('against'),
			PaymentReference.reference_name.as_('against_reference'),
			PaymentReference.reference_name.as_('order_id'),
			PaymentEntry.paid_amount.as_('amount')
		)
		.where(PaymentEntry.mode_of_payment == 'Cash')
		.where(PaymentReference.reference_doctype != 'Wallet Transaction')
		.where(PaymentEntry.docstatus == 1)
		.where(PaymentEntry.payment_type == 'Receive')
	)

	if filters.get('from_date'):
		query = query.where(PaymentEntry.modified >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(PaymentEntry.modified <= filters.get('to_date'))

	query = query.orderby(PaymentEntry.creation, order=frappe.qb.desc)

	ret_data = query.run(as_dict=True)
	result = []
	for x in ret_data:
		order_id = x.order_id
		if x.against == "Sales Invoice":
			order_id = frappe.db.get_value("Sales Invoice", x.against_reference, "reference") or x.against_reference

		cash_collection_date = None
		order_delivery = frappe.db.get_all(
			"Order Delivery Slot",
			filters={"order": order_id},
			fields=['order_date'],
			limit=1
		)
		if order_delivery:
			cash_collection_date = order_delivery[0].order_date
		else:
			cash_collection_date = frappe.db.get_value("Order", order_id, "order_date")

		result.append([
			cash_collection_date,
			x.cash_approval_date,
			x.customer,
			x.customer_name,
			x.against,
			x.against_reference,
			order_id,
			x.amount
		])
	return result
