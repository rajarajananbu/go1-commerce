# Copyright (c) 2023, Tridotstech and contributors
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
		_("Posted Date") + ":Date:120",
		_("Posted Time") + ":Data:120",
		_("Order ID") + ":Link/Order:150",
		_("Customer Name") + ":Data:200",
		_("Mode Of Payment") + ":Data:150",
		_("Transaction Type") + ":Data:120",
		_("Transaction ID") + ":Data:200",
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
			Function('DATE', PaymentEntry.creation).as_('posted_date'),
			Function('DATE_FORMAT', PaymentEntry.creation, '%h:%i %p').as_('posted_time'),
			PaymentReference.reference_name.as_('reference_name'),
			PaymentReference.reference_doctype.as_('reference_doctype'),
			CustomerDT.full_name.as_('customer_name'),
			PaymentEntry.mode_of_payment,
			PaymentEntry.payment_type,
			PaymentEntry.reference_no.as_('transaction_id'),
			PaymentReference.allocated_amount.as_('amount')
		)
		.where(PaymentEntry.docstatus == 1)
	)

	if filters.get('from_date'):
		query = query.where(PaymentEntry.posting_date >= filters.get('from_date'))
	if filters.get('to_date'):
		query = query.where(PaymentEntry.posting_date <= filters.get('to_date'))

	query = query.orderby(PaymentEntry.creation, order=frappe.qb.desc)
	raw_data = query.run(as_dict=True)

	result = []
	for row in raw_data:
		order_id = row.reference_name
		if row.reference_doctype == "Sales Invoice":
			order_id = frappe.db.get_value("Sales Invoice", row.reference_name, "reference") or row.reference_name
		elif row.reference_doctype == "Wallet Transaction":
			wt = frappe.db.get_value("Wallet Transaction", row.reference_name, ["order_type", "order_id"], as_dict=True)
			if wt:
				if wt.order_type == "Sales Invoice":
					order_id = frappe.db.get_value("Sales Invoice", wt.order_id, "reference") or wt.order_id
				else:
					order_id = wt.order_id or row.reference_name

		mode_of_payment = row.mode_of_payment
		if row.mode_of_payment == "Cash":
			if row.payment_type == "Pay":
				mode_of_payment = "Wallet"
			elif row.reference_doctype == "Wallet Transaction":
				mode_of_payment = "Wallet"

		transaction_type = "Debit" if row.payment_type == "Pay" else "Credit"

		result.append([
			row.posted_date,
			row.posted_time,
			order_id,
			row.customer_name,
			mode_of_payment,
			transaction_type,
			row.transaction_id,
			row.amount
		])

	return result
