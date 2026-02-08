# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductEnquiry(Document):
	def after_insert(self):
		frappe.publish_realtime('update_menu', {'docname': self.name,'doctype':'Product Enquiry'})
