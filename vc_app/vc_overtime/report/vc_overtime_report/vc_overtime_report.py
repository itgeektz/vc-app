import frappe
from frappe import _
from frappe.utils import flt, getdate
from vc_app.vc_overtime.overtime_calculator import calculate_overtime_for_attendance

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Define report columns with checkbox as first column"""
    return [
        {
            "label": _("Select"),
            "fieldname": "select_row",
            "fieldtype": "Check",
            "width": 50
        },
        {
            "label": _("Attendance"),
            "fieldname": "attendance",
            "fieldtype": "Link",
            "options": "Attendance",
            "width": 150
        },
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 160
        },
        {
            "label": _("Date"),
            "fieldname": "attendance_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("In Time"),
            "fieldname": "in_time",
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "label": _("Out Time"),
            "fieldname": "out_time",
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "label": _("OT Hours"),
            "fieldname": "overtime_hours",
            "fieldtype": "Float",
            "width": 90,
            "precision": 2
        },
        {
            "label": _("OT Type"),
            "fieldname": "overtime_type",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("Eligible"),
            "fieldname": "is_eligible",
            "fieldtype": "Check",
            "width": 70
        },
        {
            "label": _("Hourly Rate"),
            "fieldname": "hourly_rate",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": _("OT Rate"),
            "fieldname": "ot_rate",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": _("OT Amount"),
            "fieldname": "overtime_amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        }
    ]

def get_data(filters):
    """
    Get attendance data and calculate overtime dynamically.
    """
    if not filters:
        filters = {}
    
    conditions = get_conditions(filters)
    
    # Get attendance records
    data = frappe.db.sql(f"""
        SELECT 
            a.name as attendance,
            a.employee,
            e.employee_name,
            e.department,
            a.attendance_date,
            a.in_time,
            a.out_time,
            a.company,
            e.eligible_for_overtime as is_eligible
        FROM `tabAttendance` a
        INNER JOIN `tabEmployee` e ON a.employee = e.name
        WHERE a.docstatus = 1
            AND a.status = 'Present'
            AND a.out_time IS NOT NULL
            {conditions}
        ORDER BY a.attendance_date DESC, e.employee_name
    """, filters, as_dict=1)
    
    # Calculate overtime for each row dynamically
    for row in data:
        # Add checkbox field (unchecked by default)
        row['select_row'] = 0
        
        # Calculate OT on-the-fly
        ot_calc = calculate_overtime_for_attendance(row)
        
        # Add calculated fields to row
        row['overtime_hours'] = ot_calc['overtime_hours']
        row['overtime_type'] = ot_calc['overtime_type']
        row['hourly_rate'] = ot_calc['hourly_rate']
        row['overtime_multiplier'] = ot_calc['overtime_multiplier']
        row['overtime_amount'] = ot_calc['overtime_amount']
        row['ot_rate'] = flt(ot_calc['hourly_rate'] * ot_calc['overtime_multiplier'], 2)
        
        # Check if already processed (Additional Salary exists)
        additional_salary = frappe.db.exists("Additional Salary", {
            "employee": row['employee'],
            "payroll_date": row['attendance_date'],
            "is_overtime_salary": 1,
            "docstatus": ["<", 2]
        })
        
        if additional_salary:
            row['status'] = "Approved & Paid"
        elif ot_calc['overtime_hours'] > 0:
            row['status'] = "Pending Review"
        else:
            row['status'] = "No Overtime"
    
    # Filter out records with no overtime
    data = [d for d in data if d.get('overtime_hours', 0) > 0]
    
    return data

def get_conditions(filters):
    """Build SQL WHERE conditions from filters"""
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("AND a.attendance_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("AND a.attendance_date <= %(to_date)s")
    
    if filters.get("employee"):
        conditions.append("AND a.employee = %(employee)s")
    
    if filters.get("department"):
        conditions.append("AND e.department = %(department)s")
    
    if filters.get("company"):
        conditions.append("AND a.company = %(company)s")
    
    if filters.get("eligible_for_overtime") == "Yes":
        conditions.append("AND e.eligible_for_overtime = 1")
    elif filters.get("eligible_for_overtime") == "No":
        conditions.append("AND e.eligible_for_overtime = 0")
    
    return " ".join(conditions)