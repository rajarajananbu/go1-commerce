# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Function, Sum

month_list = ["January", "February", "March", "April", "May", "June",
			  "July", "August", "September", "October", "November", "December"]

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart

def get_columns():
	return [
		{
			"fieldname": "month",
			"fieldtype": "Data",
			"label": _("Month"),
			"width": 120
		},
		{
			"fieldname": "income_amount",
			"fieldtype": "Currency",
			"label": _("Income Amount"),
			"width": 150
		},
		{
			"fieldname": "expense_amount",
			"fieldtype": "Currency",
			"label": _("Expense Amount"),
			"width": 150
		},
		{
			"fieldname": "balance_amount",
			"fieldtype": "Currency",
			"label": _("Balance Amount"),
			"width": 150
		}
	]

def get_data(filters):
	data = []
	income_entries = get_payment_entries(filters, "Receive")
	expense_entries = get_payment_entries(filters, "Pay")
	for item in month_list:
		income, expense = 0, 0
		check_income = next((x for x in income_entries if x.month == item), None)
		check_expense = next((x for x in expense_entries if x.month == item), None)
		if check_income:
			income = float(check_income.amount or 0)
		if check_expense:
			expense = float(check_expense.amount or 0)
		balance = income - expense
		data.append([item, income, expense, balance])
	return data

def get_payment_entries(filters, payment_type):
	PaymentEntry = DocType('Payment Entry')
	query = (
		frappe.qb.from_(PaymentEntry)
		.select(
			Function('MONTHNAME', PaymentEntry.posting_date).as_('month'),
			Sum(PaymentEntry.paid_amount).as_('amount')
		)
		.where(PaymentEntry.docstatus == 1)
		.where(PaymentEntry.payment_type == payment_type)
	)
	if filters.get('year'):
		query = query.where(
			Function('YEAR', PaymentEntry.posting_date) == int(filters.get('year'))
		)
	query = query.groupby(Function('MONTHNAME', PaymentEntry.posting_date))
	return query.run(as_dict=True)

def get_chart(data):
	income_list = [x[1] for x in data]
	expense_list = [x[2] for x in data]
	return {
		"data": {
			"labels": month_list,
			"datasets": [
				{"name": _("Income"), "values": income_list},
				{"name": _("Expense"), "values": expense_list}
			]
		},
		"type": "bar",
		"colors": ["#4CAF50", "#FF5252"]
	}

@frappe.whitelist()
def get_year_list():
	PaymentEntry = DocType('Payment Entry')
	query = (
		frappe.qb.from_(PaymentEntry)
		.select(Function('YEAR', PaymentEntry.posting_date).as_('year'))
		.where(PaymentEntry.docstatus == 1)
		.distinct()
		.orderby(Function('YEAR', PaymentEntry.posting_date), order=frappe.qb.desc)
	)
	result = query.run(as_dict=True)
	return [str(row.year) for row in result] if result else [str(frappe.utils.getdate().year)]
