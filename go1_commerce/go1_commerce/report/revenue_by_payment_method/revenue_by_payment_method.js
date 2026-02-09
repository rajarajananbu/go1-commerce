// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Revenue By Payment Method"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
}
