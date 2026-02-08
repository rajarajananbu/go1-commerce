# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductAttribute(Document):
	def validate(self):
		self.unique_name=frappe.scrub(self.attribute_name)

	def on_update(self):
		self.unique_name=frappe.scrub(self.attribute_name)
