#!/bin/bash

# =====================================================================
# Complete VC Overtime App Setup Script
# Run from: ~/frappe-bench/apps/vc_app
# =====================================================================

set -e

echo "========================================"
echo "VC Overtime App - Complete Setup"
echo "========================================"

cd ~/frappe-bench/apps/vc_app

# =====================================================================
# Step 1: Create proper directory structure
# =====================================================================

echo ""
echo "Step 1: Creating directory structure..."

mkdir -p vc_app/vc_overtime/doctype/employee_ot_settings
mkdir -p vc_app/vc_overtime/doctype/overtime_record
mkdir -p vc_app/vc_overtime/doctype/employee_ot_assignment
mkdir -p vc_app/vc_overtime/doctype/employee_ot_assignment_item

# Create __init__.py files
touch vc_app/vc_overtime/__init__.py
touch vc_app/vc_overtime/doctype/employee_ot_settings/__init__.py
touch vc_app/vc_overtime/doctype/overtime_record/__init__.py
touch vc_app/vc_overtime/doctype/employee_ot_assignment/__init__.py
touch vc_app/vc_overtime/doctype/employee_ot_assignment_item/__init__.py

echo "✓ Directory structure created"

# =====================================================================
# Step 2: Update modules.txt
# =====================================================================

echo ""
echo "Step 2: Updating modules.txt..."

echo "VC Overtime" > vc_app/modules.txt

echo "✓ modules.txt updated"

# =====================================================================
# Step 3: Create all doctype JSON files
# =====================================================================

echo ""
echo "Step 3: Creating doctype JSON files..."

# Employee OT Settings
cat > vc_app/vc_overtime/doctype/employee_ot_settings/employee_ot_settings.json << 'EOTJSON'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:EMP-OT-{employee}-{#####}",
 "creation": "2024-12-11 10:00:00",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "employee",
  "employee_name",
  "eligible_for_overtime",
  "column_break_3",
  "from_date",
  "to_date",
  "section_break_5",
  "default_overtime_rate",
  "holiday_overtime_multiplier",
  "weekday_overtime_multiplier",
  "section_break_8",
  "notes"
 ],
 "fields": [
  {
   "fieldname": "employee",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Employee",
   "options": "Employee",
   "reqd": 1
  },
  {
   "fetch_from": "employee.employee_name",
   "fieldname": "employee_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Employee Name",
   "read_only": 1
  },
  {
   "default": "0",
   "fieldname": "eligible_for_overtime",
   "fieldtype": "Check",
   "in_list_view": 1,
   "label": "Eligible for Overtime"
  },
  {
   "fieldname": "column_break_3",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "from_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "label": "From Date",
   "reqd": 1
  },
  {
   "fieldname": "to_date",
   "fieldtype": "Date",
   "label": "To Date"
  },
  {
   "fieldname": "section_break_5",
   "fieldtype": "Section Break",
   "label": "Overtime Rates"
  },
  {
   "fieldname": "default_overtime_rate",
   "fieldtype": "Currency",
   "label": "Default Hourly Overtime Rate"
  },
  {
   "default": "2.0",
   "fieldname": "holiday_overtime_multiplier",
   "fieldtype": "Float",
   "label": "Holiday Overtime Multiplier",
   "precision": "2"
  },
  {
   "default": "1.5",
   "fieldname": "weekday_overtime_multiplier",
   "fieldtype": "Float",
   "label": "Weekday Overtime Multiplier",
   "precision": "2"
  },
  {
   "fieldname": "section_break_8",
   "fieldtype": "Section Break"
  },
  {
   "fieldname": "notes",
   "fieldtype": "Text",
   "label": "Notes"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2024-12-11 10:00:00",
 "modified_by": "Administrator",
 "module": "VC Overtime",
 "name": "Employee OT Settings",
 "naming_rule": "Expression",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "HR Manager",
   "share": 1,
   "write": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "employee_name",
 "track_changes": 1
}
EOTJSON

echo "✓ Created employee_ot_settings.json"

# Overtime Record
cat > vc_app/vc_overtime/doctype/overtime_record/overtime_record.json << 'ORTJSON'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:OT-{employee}-{attendance_date}-{#####}",
 "creation": "2024-12-11 10:00:00",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "employee",
  "employee_name",
  "attendance",
  "column_break_3",
  "attendance_date",
  "posting_date",
  "section_break_12",
  "calculated_overtime_hours",
  "overtime_rate",
  "overtime_multiplier",
  "overtime_amount",
  "column_break_16",
  "is_holiday",
  "is_paid",
  "salary_slip"
 ],
 "fields": [
  {
   "fieldname": "employee",
   "fieldtype": "Link",
   "in_list_view": 1,
   "in_standard_filter": 1,
   "label": "Employee",
   "options": "Employee",
   "reqd": 1
  },
  {
   "fetch_from": "employee.employee_name",
   "fieldname": "employee_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Employee Name",
   "read_only": 1
  },
  {
   "fieldname": "attendance",
   "fieldtype": "Link",
   "label": "Attendance",
   "options": "Attendance"
  },
  {
   "fieldname": "column_break_3",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "attendance_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "in_standard_filter": 1,
   "label": "Attendance Date",
   "reqd": 1
  },
  {
   "default": "Today",
   "fieldname": "posting_date",
   "fieldtype": "Date",
   "label": "Posting Date"
  },
  {
   "fieldname": "section_break_12",
   "fieldtype": "Section Break",
   "label": "Overtime Calculation"
  },
  {
   "fieldname": "calculated_overtime_hours",
   "fieldtype": "Float",
   "in_list_view": 1,
   "label": "Overtime Hours",
   "precision": "2"
  },
  {
   "fieldname": "overtime_rate",
   "fieldtype": "Currency",
   "label": "Overtime Rate (per hour)"
  },
  {
   "fieldname": "overtime_multiplier",
   "fieldtype": "Float",
   "label": "Overtime Multiplier",
   "precision": "2"
  },
  {
   "fieldname": "overtime_amount",
   "fieldtype": "Currency",
   "in_list_view": 1,
   "label": "Overtime Amount"
  },
  {
   "fieldname": "column_break_16",
   "fieldtype": "Column Break"
  },
  {
   "default": "0",
   "fieldname": "is_holiday",
   "fieldtype": "Check",
   "label": "Is Holiday"
  },
  {
   "default": "0",
   "fieldname": "is_paid",
   "fieldtype": "Check",
   "label": "Is Paid"
  },
  {
   "fieldname": "salary_slip",
   "fieldtype": "Link",
   "label": "Salary Slip",
   "options": "Salary Slip"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2024-12-11 10:00:00",
 "modified_by": "Administrator",
 "module": "VC Overtime",
 "name": "Overtime Record",
 "naming_rule": "Expression",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "HR Manager",
   "share": 1,
   "write": 1
  },
  {
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "HR User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "employee_name",
 "track_changes": 1
}
ORTJSON

echo "✓ Created overtime_record.json"

# Employee OT Assignment (Simplified - no child table initially)
cat > vc_app/vc_overtime/doctype/employee_ot_assignment/employee_ot_assignment.json << 'EOAJSON'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:OT-ASSIGN-{####}",
 "creation": "2024-12-11 10:00:00",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "from_date",
  "to_date",
  "section_break_2",
  "notes"
 ],
 "fields": [
  {
   "fieldname": "from_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "label": "From Date",
   "reqd": 1
  },
  {
   "fieldname": "to_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "label": "To Date"
  },
  {
   "fieldname": "section_break_2",
   "fieldtype": "Section Break"
  },
  {
   "fieldname": "notes",
   "fieldtype": "Text",
   "label": "Notes"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2024-12-11 10:00:00",
 "modified_by": "Administrator",
 "module": "VC Overtime",
 "name": "Employee OT Assignment",
 "naming_rule": "Expression",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "HR Manager",
   "share": 1,
   "write": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
EOAJSON

echo "✓ Created employee_ot_assignment.json"

# Employee OT Assignment Item (Child table - for future use)
cat > vc_app/vc_overtime/doctype/employee_ot_assignment_item/employee_ot_assignment_item.json << 'EOAIJSON'
{
 "actions": [],
 "creation": "2024-12-11 10:00:00",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "employee",
  "employee_name"
 ],
 "fields": [
  {
   "fieldname": "employee",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Employee",
   "options": "Employee",
   "reqd": 1
  },
  {
   "fetch_from": "employee.employee_name",
   "fieldname": "employee_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Employee Name",
   "read_only": 1
  }
 ],
 "index_web_pages_for_search": 1,
 "istable": 1,
 "links": [],
 "modified": "2024-12-11 10:00:00",
 "modified_by": "Administrator",
 "module": "VC Overtime",
 "name": "Employee OT Assignment Item",
 "owner": "Administrator",
 "permissions": [],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": []
}
EOAIJSON

echo "✓ Created employee_ot_assignment_item.json"

# =====================================================================
# Step 4: Create Python controller files
# =====================================================================

echo ""
echo "Step 4: Creating Python controller files..."

# employee_ot_settings.py
cat > vc_app/vc_overtime/doctype/employee_ot_settings/employee_ot_settings.py << 'EOTPY'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeOTSettings(Document):
    def validate(self):
        if self.to_date and self.from_date > self.to_date:
            frappe.throw("To Date cannot be before From Date")
EOTPY

# overtime_record.py
cat > vc_app/vc_overtime/doctype/overtime_record/overtime_record.py << 'ORTPY'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class OvertimeRecord(Document):
    def validate(self):
        if self.calculated_overtime_hours and self.overtime_rate:
            if not self.overtime_multiplier:
                self.overtime_multiplier = 1.5
            self.overtime_amount = flt(
                self.calculated_overtime_hours * 
                self.overtime_rate * 
                self.overtime_multiplier,
                2
            )
ORTPY

# employee_ot_assignment.py
cat > vc_app/vc_overtime/doctype/employee_ot_assignment/employee_ot_assignment.py << 'EOAPY'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeOTAssignment(Document):
    pass
EOAPY

# employee_ot_assignment_item.py
cat > vc_app/vc_overtime/doctype/employee_ot_assignment_item/employee_ot_assignment_item.py << 'EOAIPY'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeOTAssignmentItem(Document):
    pass
EOAIPY

echo "✓ Python controller files created"

echo ""
echo "========================================"
echo "✓ All files created successfully!"
echo "========================================"
echo ""
echo "Now run these commands:"
echo ""
echo "  cd ~/frappe-bench"
echo "  bench --site mysite clear-cache"
echo "  bench build --app vc_app"
echo "  bench --site mysite migrate"
echo "  bench restart"
echo ""
echo "========================================"
