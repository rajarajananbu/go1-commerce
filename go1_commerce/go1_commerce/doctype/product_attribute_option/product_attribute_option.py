# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProductAttributeOption(Document):
	def validate(self):		
		self.make_unique_name()
		
	def make_unique_name(self):		
		self.unique_name=frappe.scrub(self.option_value)
		