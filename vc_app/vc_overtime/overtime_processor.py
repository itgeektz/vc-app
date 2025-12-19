# =====================================================================
# FILE: vc_app/vc_overtime/overtime_processor.py
# UPDATED: Now handles approved_overtime_hours from frontend
# =====================================================================

import frappe
from frappe import _
from frappe.utils import flt, getdate, add_to_date, get_datetime, time_diff_in_hours
import hashlib
from datetime import datetime
from vc_app.vc_overtime.overtime_calculator import (
    calculate_overtime_for_attendance,
    get_shift_details,
    get_overtime_multiplier
)
import random 

# =====================================================================
# MAIN PROCESSING FUNCTION
# =====================================================================

@frappe.whitelist()
def process_selected_overtime(attendance_list, action="approve"):
    """
    Process selected overtime records.
    
    Args:
        attendance_list: JSON string or list - can be:
            - Simple list: ["ATT-001", "ATT-002"]
            - Dictionary list: [{"attendance": "ATT-001", "approved_overtime_hours": 2.5, "has_custom_hours": True}, ...]
        action: "approve" or "reject"
    
    Returns:
        dict with results
    """
    import json
    
    # Convert JSON to list if needed
    if isinstance(attendance_list, str):
        attendance_list = json.loads(attendance_list)
    
    if not attendance_list:
        frappe.throw(_("No attendance records selected"))
    
    results = {
        "processed": 0,
        "approved": 0,
        "rejected": 0,
        "errors": []
    }
    
    for item in attendance_list:
        try:
            # Handle both old format (string) and new format (dict)
            if isinstance(item, dict):
                att_name = item.get('attendance')
                approved_hours = flt(item.get('approved_overtime_hours', 0))
                has_custom_hours = item.get('has_custom_hours', False)
            else:
                # Old format - simple string
                att_name = item
                approved_hours = 0  # Will be calculated
                has_custom_hours = False
            
            # Get attendance data
            att_data = frappe.db.get_value("Attendance", att_name, 
                ["employee", "attendance_date", "in_time", "out_time", "company"], 
                as_dict=True
            )
            
            if not att_data:
                results["errors"].append(f"{att_name}: Attendance not found")
                continue
            
            if not att_data.get('out_time'):
                results["errors"].append(f"{att_name}: No checkout time recorded")
                continue
            
            if action == "approve":
                # Approve and create Additional Salary
                approve_overtime(att_name, att_data, approved_hours, has_custom_hours)
                results["approved"] += 1
                results["processed"] += 1
            elif action == "reject":
                # Reject and reset time
                reject_overtime(att_name, att_data, approved_hours, has_custom_hours)
                results["rejected"] += 1
                results["processed"] += 1
            else:
                results["errors"].append(f"{att_name}: Invalid action '{action}'")
            
        except Exception as e:
            error_msg = f"{att_name if 'att_name' in locals() else 'Unknown'}: {str(e)}"
            results["errors"].append(error_msg)
            frappe.log_error(error_msg, "Overtime Processing Error")
    
    frappe.db.commit()
    
    return results


# =====================================================================
# APPROVE OVERTIME
# =====================================================================

def approve_overtime(attendance_name, att_data, approved_hours=0, has_custom_hours=False):
    """
    Approve overtime and create Additional Salary.
    
    Args:
        attendance_name: Attendance document name
        att_data: Attendance data dict
        approved_hours: Manually approved hours (0 = use calculated)
        has_custom_hours: Whether hours were manually edited
    """
    # Check eligibility
    is_eligible = frappe.db.get_value("Employee", att_data['employee'], "eligible_for_overtime")
    
    if not is_eligible:
        frappe.throw(_("Employee {0} is not eligible for overtime").format(att_data['employee']))
    
    # Calculate overtime
    ot_calc = calculate_overtime_for_attendance(att_data)
    
    if not ot_calc.get('is_eligible'):
        frappe.throw(_("Employee {0} is not eligible for overtime").format(att_data['employee']))
    
    # Use approved hours if provided, otherwise use calculated
    if has_custom_hours and approved_hours > 0:
        final_hours = approved_hours
        frappe.msgprint(
            _("Using manually approved hours: {0} (calculated: {1})").format(
                final_hours, ot_calc['overtime_hours']
            ),
            alert=True,
            indicator="blue"
        )
    else:
        final_hours = ot_calc['overtime_hours']
    
    if final_hours <= 0:
        frappe.throw(_("No overtime hours to approve. Allowance: {0} minutes").format(
            ot_calc['allowance_minutes']
        ))
    
    # Calculate amount based on final hours
    final_amount = flt(final_hours * ot_calc['hourly_rate'] * ot_calc['overtime_multiplier'], 2)
    
    if final_amount <= 0:
        frappe.throw(_("No overtime amount calculated for this attendance"))
    
    # Check if already approved
    existing = frappe.db.exists("Additional Salary", {
        "employee": att_data['employee'],
        "payroll_date": att_data['attendance_date'],
        "is_overtime_salary": 1,
        "docstatus": ["<", 2]
    })
    
    if existing:
        frappe.throw(_("Additional Salary already exists for this overtime on {0}").format(
            att_data['attendance_date']
        ))
    
    # Get salary component
    if ot_calc['overtime_type'] in ["Holiday", "Sunday"]:
        component = frappe.db.get_single_value("HR Settings", "holiday_overtime_component")
    else:
        component = frappe.db.get_single_value("HR Settings", "weekday_overtime_component")
    
    if not component:
        frappe.throw(_("Overtime salary component not configured in HR Settings"))
    
    # Verify component exists
    if not frappe.db.exists("Salary Component", component):
        frappe.throw(_("Salary Component {0} does not exist").format(component))
    
    # Create Additional Salary
    add_sal = frappe.new_doc("Additional Salary")
    add_sal.employee = att_data['employee']
    add_sal.company = att_data['company']
    add_sal.salary_component = component
    add_sal.amount = final_amount
    add_sal.payroll_date = att_data['attendance_date']
    add_sal.overwrite_salary_structure_amount = 0
    
    # Custom fields (if they exist)
    if hasattr(add_sal, 'is_overtime_salary'):
        add_sal.is_overtime_salary = 1
    if hasattr(add_sal, 'overtime_hours'):
        add_sal.overtime_hours = final_hours
    if hasattr(add_sal, 'overtime_type'):
        add_sal.overtime_type = ot_calc['overtime_type']
    if hasattr(add_sal, 'overtime_attendance'):
        add_sal.overtime_attendance = attendance_name
    
    # Save and submit
    add_sal.insert(ignore_permissions=True)
    add_sal.submit()
    
    # If custom hours used, also reset the checkout time to match
    if has_custom_hours and approved_hours > 0:
        reset_time_to_approved_hours(attendance_name, att_data, approved_hours, ot_calc)
    
    frappe.msgprint(
        _("Created Additional Salary {0} for {1}: KES {2} ({3} OT hours{4})").format(
            add_sal.name,
            att_data['employee'],
            frappe.format_value(final_amount, {"fieldtype": "Currency"}),
            final_hours,
            " - custom approved" if has_custom_hours else ""
        ),
        alert=True
    )


# =====================================================================
# REJECT OVERTIME
# =====================================================================

def reject_overtime(attendance_name, att_data, approved_hours=0, has_custom_hours=False):
    """
    Reject overtime and reset checkout time.
    Now uses approved_hours if provided for reset calculation.
    
    Args:
        attendance_name: Attendance document name
        att_data: Attendance data dict
        approved_hours: Hours to reset to (0 = standard reset)
        has_custom_hours: Whether to use approved hours for reset
    """
    # Get shift details including allowance
    shift_details = get_shift_details(att_data['employee'], att_data['attendance_date'])
    
    if not shift_details:
        frappe.throw(_("Cannot determine shift details for employee {0}").format(
            att_data['employee']
        ))
    
    # Get in_time
    in_time = get_datetime(att_data['in_time'])
    
    # Calculate reset time based on approved hours or standard
    if has_custom_hours and approved_hours > 0:
        # Use approved hours: in_time + 8 hrs + approved_hrs + allowance + variance
        reset_time = add_to_date(in_time, hours=8)
        reset_time = add_to_date(reset_time, hours=approved_hours)
        
        # Add allowance
        allowance_minutes = shift_details['overtime_allowance_minutes']
        random_minutes = random.randint(0, allowance_minutes) if allowance_minutes > 0 else 0
        reset_time = add_to_date(reset_time, minutes=random_minutes)
        
        # Add ±5 minutes variance for custom hours
        variance_minutes = random.randint(-5, 5)
        reset_time = add_to_date(reset_time, minutes=variance_minutes)
        
        reset_type = f"approved {approved_hours} hrs"
    else:
        # Standard reset: in_time + 8 hours + allowance + 3-4 sec variance
        reset_time = add_to_date(in_time, hours=8)
        
        # Add random portion of allowance
        allowance_minutes = shift_details['overtime_allowance_minutes']
        random_minutes = random.randint(0, allowance_minutes) if allowance_minutes > 0 else 0
        reset_time = add_to_date(reset_time, minutes=random_minutes)
        
        # Add 3-4 second variance
        variance_seconds = calculate_variance_seconds(att_data['employee'], att_data['attendance_date'])
        reset_time = add_to_date(reset_time, seconds=variance_seconds)
        
        reset_type = "standard (no OT)"
    
    # Calculate the new worked hours after reset
    new_worked_hours = time_diff_in_hours(reset_time, in_time)
    
    # Ensure at least 8 hours worked
    if new_worked_hours < 8:
        reset_time = add_to_date(in_time, hours=8, seconds=variance_seconds if not has_custom_hours else 0)
        new_worked_hours = 8.0
    
    # Find the most recent OUT checkin for this attendance
    out_checkin = frappe.db.sql("""
        SELECT name, time
        FROM `tabEmployee Checkin`
        WHERE employee = %s
            AND attendance = %s
            AND log_type = 'OUT'
        ORDER BY time DESC
        LIMIT 1
    """, (att_data['employee'], attendance_name), as_dict=True)
    
    if not out_checkin:
        # Try without attendance link
        out_checkin = frappe.db.sql("""
            SELECT name, time
            FROM `tabEmployee Checkin`
            WHERE employee = %s
                AND log_type = 'OUT'
                AND DATE(time) = %s
            ORDER BY time DESC
            LIMIT 1
        """, (att_data['employee'], att_data['attendance_date']), as_dict=True)
    
    if out_checkin:
        frappe.db.set_value(
            "Employee Checkin",
            out_checkin[0].name,
            {
                "time": reset_time,
                "skip_auto_attendance": 1  # Prevent re-processing
            }
        )
    
    # Update Attendance out_time
    frappe.db.set_value(
        "Attendance",
        attendance_name,
        "out_time",
        reset_time
    )
    
    # Update working hours
    frappe.db.set_value(
        "Attendance",
        attendance_name,
        "working_hours",
        flt(new_worked_hours, 2)
    )
    
    frappe.msgprint(
        _("Reset checkout time for {0} to {1}<br>New worked hours: {2}<br>Reset type: {3}").format(
            att_data['employee'],
            reset_time.strftime("%Y-%m-%d %H:%M:%S"),
            flt(new_worked_hours, 2),
            reset_type
        ),
        alert=True
    )


def reset_time_to_approved_hours(attendance_name, att_data, approved_hours, ot_calc):
    """
    Reset checkout time to match approved hours (used when approving with custom hours).
    Formula: in_time + 8 hrs + approved_hrs + allowance ± 5 min
    """
    # Get shift details
    shift_details = get_shift_details(att_data['employee'], att_data['attendance_date'])
    
    if not shift_details:
        return
    
    # Get in_time
    in_time = get_datetime(att_data['in_time'])
    
    # Calculate new checkout time
    # Base: in_time + 8 hours (standard work day)
    new_out_time = add_to_date(in_time, hours=8)
    
    # Add approved overtime hours
    new_out_time = add_to_date(new_out_time, hours=approved_hours)
    
    # Add allowance
    allowance_minutes = shift_details['overtime_allowance_minutes']
    random_minutes = random.randint(0, allowance_minutes) if allowance_minutes > 0 else 0
    new_out_time = add_to_date(new_out_time, minutes=random_minutes)
    
    # Add ±5 minutes variance
    variance_minutes = random.randint(-5, 5)
    new_out_time = add_to_date(new_out_time, minutes=variance_minutes)
    
    # Update Employee Checkin
    out_checkin = frappe.db.sql("""
        SELECT name
        FROM `tabEmployee Checkin`
        WHERE employee = %s
            AND attendance = %s
            AND log_type = 'OUT'
        ORDER BY time DESC
        LIMIT 1
    """, (att_data['employee'], attendance_name), as_dict=True)
    
    if out_checkin:
        frappe.db.set_value(
            "Employee Checkin",
            out_checkin[0].name,
            {
                "time": new_out_time,
                "skip_auto_attendance": 1
            }
        )
    
    # Update Attendance
    new_worked_hours = time_diff_in_hours(new_out_time, in_time)
    frappe.db.set_value(
        "Attendance",
        attendance_name,
        {
            "out_time": new_out_time,
            "working_hours": flt(new_worked_hours, 2)
        }
    )
    
    frappe.msgprint(
        _("Adjusted checkout time to match approved hours:<br>New out time: {0}<br>Total hours: {1}").format(
            new_out_time.strftime("%Y-%m-%d %H:%M:%S"),
            flt(new_worked_hours, 2)
        ),
        alert=True,
        indicator="blue"
    )


def calculate_variance_seconds(employee, date):
    """
    Calculate deterministic variance (3-4 seconds) based on employee + date.
    This ensures each employee gets a unique but consistent reset time.
    """
    hash_input = f"{employee}{date}".encode()
    hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
    variance_seconds = (hash_value % 2) + 3  # Returns 3 or 4
    return variance_seconds


# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

@frappe.whitelist()
def get_overtime_details(attendance_name):
    """
    Get calculated overtime details for a single attendance.
    Used for verification.
    """
    att_data = frappe.db.get_value("Attendance", attendance_name,
        ["employee", "attendance_date", "in_time", "out_time", "company"],
        as_dict=True
    )
    
    if not att_data:
        return None
    
    # Calculate overtime
    ot_calc = calculate_overtime_for_attendance(att_data)
    
    # Check if already approved
    additional_salary = frappe.db.get_value("Additional Salary", {
        "employee": att_data['employee'],
        "payroll_date": att_data['attendance_date'],
        "is_overtime_salary": 1,
        "docstatus": ["<", 2]
    }, ["name", "amount"], as_dict=True)
    
    return {
        "overtime_hours": ot_calc['overtime_hours'],
        "overtime_type": ot_calc['overtime_type'],
        "hourly_rate": ot_calc['hourly_rate'],
        "overtime_amount": ot_calc['overtime_amount'],
        "overtime_threshold": ot_calc['overtime_threshold'],
        "allowance_minutes": ot_calc['allowance_minutes'],
        "is_eligible": ot_calc['is_eligible'],
        "is_approved": bool(additional_salary),
        "additional_salary": additional_salary.name if additional_salary else None
    }