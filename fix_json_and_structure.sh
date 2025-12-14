#!/bin/bash

# =====================================================================
# Fix Invalid JSON Files and Create Proper Doctype Structure
# =====================================================================

echo "Checking for invalid JSON files..."

cd ~/frappe-bench/apps/vc_app

# Find and check all JSON files
find vc_app/vc_overtime/doctype -name "*.json" -type f | while read json_file; do
    if [ ! -s "$json_file" ]; then
        echo "⚠ Empty file found: $json_file"
    else
        if ! python3 -m json.tool "$json_file" > /dev/null 2>&1; then
            echo "✗ Invalid JSON: $json_file"
        else
            echo "✓ Valid: $json_file"
        fi
    fi
done

echo ""
echo "Creating complete doctype files..."

# =====================================================================
# Create employee_ot_settings.json
# =====================================================================

cat > vc_app/vc_overtime/doctype/employee_ot_settings/employee_ot_settings.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:EMP-OT-{employee}-{from_date}",
 "creation": "2024-12-11 10:00:00.000000",
 "doctype": "DocType",
 "editable_grid": 1,
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
 "modified": "2024-12-11 10:00:00.000000",
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
  },
  {
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "HR User",
   "share": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "employee_name",
 "track_changes": 1
}
EOF

# =====================================================================
# Create overtime_record.json
# =====================================================================

cat > vc_app/vc_overtime/doctype/overtime_record/overtime_record.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:OT-{employee}-{attendance_date}",
 "creation": "2024-12-11 10:00:00.000000",
 "doctype": "DocType",
 "editable_grid": 1,
 "engine": "InnoDB",
 "field_order": [
  "employee",
  "employee_name",
  "attendance",
  "column_break_3",
  "attendance_date",
  "posting_date",
  "payroll_period",
  "section_break_5",
  "shift_start",
  "shift_end",
  "actual_in_time",
  "actual_out_time",
  "column_break_9",
  "effective_out_time",
  "reset_close_time",
  "variance_seconds",
  "section_break_12",
  "calculated_overtime_hours",
  "overtime_rate",
  "overtime_multiplier",
  "overtime_amount",
  "column_break_16",
  "is_holiday",
  "is_paid",
  "salary_slip",
  "section_break_19",
  "notes"
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
   "fieldname": "payroll_period",
   "fieldtype": "Link",
   "label": "Payroll Period",
   "options": "Payroll Period"
  },
  {
   "fieldname": "section_break_5",
   "fieldtype": "Section Break",
   "label": "Time Details"
  },
  {
   "fieldname": "shift_start",
   "fieldtype": "Time",
   "label": "Shift Start"
  },
  {
   "fieldname": "shift_end",
   "fieldtype": "Time",
   "label": "Shift End"
  },
  {
   "fieldname": "actual_in_time",
   "fieldtype": "Datetime",
   "label": "Actual In Time"
  },
  {
   "fieldname": "actual_out_time",
   "fieldtype": "Datetime",
   "label": "Actual Out Time"
  },
  {
   "fieldname": "column_break_9",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "effective_out_time",
   "fieldtype": "Datetime",
   "label": "Effective Out Time (for OT)"
  },
  {
   "fieldname": "reset_close_time",
   "fieldtype": "Datetime",
   "label": "Reset Close Time (Non-OT)"
  },
  {
   "fieldname": "variance_seconds",
   "fieldtype": "Int",
   "label": "Variance Seconds (3-4s)"
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
  },
  {
   "fieldname": "section_break_19",
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
 "modified": "2024-12-11 10:00:00.000000",
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
   "role": "HR User",
   "share": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "employee_name",
 "track_changes": 1
}
EOF

# =====================================================================
# Create employee_ot_assignment.json
# =====================================================================

cat > vc_app/vc_overtime/doctype/employee_ot_assignment/employee_ot_assignment.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "format:OT-ASSIGN-{####}",
 "creation": "2024-12-11 10:00:00.000000",
 "doctype": "DocType",
 "editable_grid": 1,
 "engine": "InnoDB",
 "field_order": [
  "from_date",
  "to_date",
  "section_break_2",
  "employees"
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
   "fieldname": "employees",
   "fieldtype": "Table",
   "label": "Employees",
   "options": "Employee OT Assignment Item"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2024-12-11 10:00:00.000000",
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
EOF

# =====================================================================
# Create Python files if they don't exist
# =====================================================================

# employee_ot_settings.py
cat > vc_app/vc_overtime/doctype/employee_ot_settings/employee_ot_settings.py << 'EOF'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeOTSettings(Document):
    def validate(self):
        if self.to_date and self.from_date > self.to_date:
            frappe.throw("To Date cannot be before From Date")
EOF

# overtime_record.py
cat > vc_app/vc_overtime/doctype/overtime_record/overtime_record.py << 'EOF'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OvertimeRecord(Document):
    def validate(self):
        if self.calculated_overtime_hours and self.overtime_rate:
            if not self.overtime_multiplier:
                self.overtime_multiplier = 1.5
            self.overtime_amount = (
                self.calculated_overtime_hours * 
                self.overtime_rate * 
                self.overtime_multiplier
            )
EOF

# employee_ot_assignment.py
cat > vc_app/vc_overtime/doctype/employee_ot_assignment/employee_ot_assignment.py << 'EOF'
# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeOTAssignment(Document):
    pass
EOF

# Create __init__.py files
touch vc_app/vc_overtime/doctype/employee_ot_settings/__init__.py
touch vc_app/vc_overtime/doctype/overtime_record/__init__.py
touch vc_app/vc_overtime/doctype/employee_ot_assignment/__init__.py

echo "✓ All doctype files created"

echo ""
echo "Validating JSON files..."

# Validate all JSON files
for json_file in vc_app/vc_overtime/doctype/*/*.json; do
    if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
        echo "✓ Valid: $(basename $json_file)"
    else
        echo "✗ Invalid: $(basename $json_file)"
        exit 1
    fi
done

echo ""
echo "All files created successfully!"
echo "Now run:"
echo "  cd ~/frappe-bench"
echo "  bench --site mysite clear-cache"
echo "  bench build --app vc_app"
echo "  bench --site mysite migrate"
EOF

chmod +x fix_json_and_structure.sh
