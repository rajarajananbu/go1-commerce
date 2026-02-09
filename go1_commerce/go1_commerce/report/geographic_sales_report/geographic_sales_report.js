// Copyright (c) 2024, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Geographic Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": ""
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": ""
		},
		{
			"fieldname": "group_by",
			"label": __("Group By"),
			"fieldtype": "Select",
			"options": "\nCity\nState\nCountry",
			"default": "City"
		}
	]
}
