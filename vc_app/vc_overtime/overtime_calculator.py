# =====================================================================
# FILE: vc_app/vc_overtime/overtime_calculator.py
# Updated with shift-specific overtime allowance/grace period
# =====================================================================

import frappe
from frappe import _
from frappe.utils import flt, cint, getdate, time_diff_in_hours, get_datetime, add_to_date
from datetime import datetime, timedelta

# =====================================================================
# CORE CALCULATION FUNCTIONS
# =====================================================================

def calculate_overtime_for_attendance(attendance_doc):
    """
    Calculate overtime dynamically from attendance data.
    Now considers shift-specific overtime allowance.
    
    Formula:
    - Total worked hours = out_time - in_time
    - Standard hours = 8
    - Overtime threshold = shift_end + overtime_allowance_minutes
    - Overtime hours = max(0, worked_hours - standard_hours - (allowance_minutes / 60))
    
    Parameters:
        attendance_doc: Attendance document or dict with:
            - employee
            - attendance_date
            - in_time
            - out_time
            - company
    
    Returns:
        dict: {
            'overtime_hours': float,
            'overtime_type': str,
            'hourly_rate': float,
            'overtime_multiplier': float,
            'overtime_amount': float,
            'is_eligible': bool,
            'shift_end': datetime,
            'overtime_threshold': datetime,
            'allowance_minutes': int
        }
    """
    result = {
        'overtime_hours': 0,
        'overtime_type': None,
        'hourly_rate': 0,
        'overtime_multiplier': 0,
        'overtime_amount': 0,
        'is_eligible': False,
        'shift_end': None,
        'overtime_threshold': None,
        'allowance_minutes': 0
    }
    
    # Get attendance data
    if isinstance(attendance_doc, dict):
        employee = attendance_doc.get('employee')
        date = attendance_doc.get('attendance_date')
        in_time = attendance_doc.get('in_time')
        out_time = attendance_doc.get('out_time')
        company = attendance_doc.get('company')
    else:
        employee = attendance_doc.employee
        date = attendance_doc.attendance_date
        in_time = attendance_doc.in_time
        out_time = attendance_doc.out_time
        company = attendance_doc.company
    
    if not out_time or not in_time:
        return result
    
    # Check eligibility
    is_eligible = frappe.db.get_value("Employee", employee, "eligible_for_overtime")
    result['is_eligible'] = bool(is_eligible)
    
    # Get shift details including overtime allowance
    shift_details = get_shift_details(employee, date)
    if not shift_details:
        return result
    
    result['shift_end'] = shift_details['end_time']
    result['allowance_minutes'] = shift_details['overtime_allowance_minutes']
    
    # Calculate overtime threshold (shift_end + allowance)
    overtime_threshold = add_to_date(
        shift_details['end_time'], 
        minutes=shift_details['overtime_allowance_minutes']
    )
    result['overtime_threshold'] = overtime_threshold
    
    # Get actual times
    in_dt = get_datetime(in_time)
    out_dt = get_datetime(out_time)
    
    # Calculate total worked hours
    total_worked_hours = time_diff_in_hours(out_dt, in_dt)
    
    # Calculate overtime hours using the formula:
    # OT = (out_time - in_time) - 8 hours - (allowance_minutes / 60)
    standard_hours = 8.0
    allowance_hours = flt(shift_details['overtime_allowance_minutes'] / 60.0, 2)
    
    overtime_hours = total_worked_hours - standard_hours - allowance_hours
    
    # Only count positive overtime
    overtime_hours = max(0, overtime_hours)
    
    if overtime_hours <= 0:
        return result
    
    result['overtime_hours'] = flt(overtime_hours, 2)
    
    # Determine overtime type
    ot_type = get_overtime_type(date, company)
    result['overtime_type'] = ot_type
    
    # Get hourly rate
    hourly_rate = get_hourly_rate(employee, date)
    result['hourly_rate'] = hourly_rate
    
    if hourly_rate <= 0:
        return result
    
    # Get multiplier
    multiplier = get_overtime_multiplier(ot_type)
    result['overtime_multiplier'] = multiplier
    
    # Calculate amount
    ot_amount = flt(overtime_hours * hourly_rate * multiplier, 2)
    result['overtime_amount'] = ot_amount
    
    return result


def get_shift_details(employee, date):
    """
    Get shift details including overtime allowance.
    
    Returns:
        dict: {
            'shift_type': str,
            'end_time': datetime,
            'overtime_allowance_minutes': int
        }
    """
    # Try shift assignment first
    shift = frappe.db.sql("""
        SELECT shift_type
        FROM `tabShift Assignment`
        WHERE employee = %s
            AND start_date <= %s
            AND docstatus = 1
        ORDER BY start_date DESC
        LIMIT 1
    """, (employee, date), as_dict=True)
    
    if shift:
        shift_type = shift[0].shift_type
    else:
        shift_type = frappe.db.get_value("Employee", employee, "default_shift")
    
    if not shift_type:
        return None
    
    # Get shift type details including overtime allowance
    shift_details = frappe.db.get_value(
        "Shift Type", 
        shift_type, 
        ["end_time", "overtime_allowance_minutes"],
        as_dict=True
    )
    
    if not shift_details or not shift_details.end_time:
        return None
    
    end_time = shift_details.end_time
    
    # Convert timedelta to time if needed
    if isinstance(end_time, datetime):
        end_time = end_time.time()
    elif hasattr(end_time, 'seconds'):
        total_seconds = int(end_time.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        end_time = datetime.min.time().replace(hour=hours, minute=minutes, second=seconds)
    
    # Combine with date
    end_datetime = datetime.combine(getdate(date), end_time)
    
    # Get overtime allowance (default to 0 if not set)
    overtime_allowance = cint(shift_details.get('overtime_allowance_minutes') or 0)
    
    return {
        'shift_type': shift_type,
        'end_time': end_datetime,
        'overtime_allowance_minutes': overtime_allowance
    }


def get_shift_end_time(employee, date):
    """
    Get shift end time for employee on date.
    Returns: datetime object or None
    
    NOTE: This function is kept for backward compatibility.
    Use get_shift_details() for new code.
    """
    shift_details = get_shift_details(employee, date)
    if shift_details:
        return shift_details['end_time']
    return None


def get_hourly_rate(employee, date):
    """
    Get hourly rate from Salary Structure Assignment.
    """
    ssa = frappe.db.sql("""
        SELECT hourly_rate, base
        FROM `tabSalary Structure Assignment`
        WHERE employee = %s
            AND docstatus = 1
            AND from_date <= %s
        ORDER BY from_date DESC
        LIMIT 1
    """, (employee, date), as_dict=True)
    
    if not ssa:
        return 0
    
    hourly_rate = ssa[0].hourly_rate
    
    # If not calculated, calculate now
    if not hourly_rate and ssa[0].base:
        standard_hours = frappe.db.get_single_value(
            "HR Settings", "standard_hours_per_month"
        ) or 225
        hourly_rate = flt(ssa[0].base / standard_hours, 2)
    
    return flt(hourly_rate, 2)


def get_overtime_type(date, company):
    """
    Determine overtime type: Normal, Holiday, or Sunday
    """
    # Check holiday
    holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
    if holiday_list:
        is_holiday = frappe.db.exists("Holiday", {
            "parent": holiday_list,
            "holiday_date": date
        })
        if is_holiday:
            return "Holiday"
    
    # Check Sunday
    if getdate(date).weekday() == 6:
        return "Sunday"
    
    return "Normal"


def get_overtime_multiplier(overtime_type):
    """
    Get multiplier based on type.
    """
    if overtime_type in ["Holiday", "Sunday"]:
        return flt(frappe.db.get_single_value(
            "HR Settings", "holiday_overtime_multiplier"
        ) or 2.0, 2)
    else:
        return flt(frappe.db.get_single_value(
            "HR Settings", "weekday_overtime_multiplier"
        ) or 1.5, 2)
    

def calculate_hourly_rate_on_save(doc, method=None):
    """
    AUTOMATIC CALCULATION: Triggered when Salary Structure Assignment is saved.
    
    PURPOSE:
    Calculate and store hourly rate based on basic salary and standard hours.
    
    FORMULA:
    Hourly Rate = Basic Salary / Standard Hours per Month
    
    EXAMPLE:
    - Basic Salary: KES 52,000
    - Standard Hours: 225 (from HR Settings)
    - Hourly Rate: 52,000 / 225 = KES 231.11
    
    PARAMETERS:
    - doc: The Salary Structure Assignment document being saved
    - method: Hook method name (not used, but required by Frappe hooks)
    
    PROCESS:
    1. Check if basic salary (base) exists and is positive
    2. Get standard hours from HR Settings (default: 225)
    3. Calculate: base / standard_hours
    4. Round to 2 decimal places using flt()
    5. Set the hourly_rate field
    
    NOTE: This runs AUTOMATICALLY every time salary is saved/updated
    """
    # Safety check: Don't calculate if no base salary
    if not doc.base or doc.base <= 0:
        return  # Exit function early
    
    # Get standard hours from HR Settings (configured during installation)
    # If not set, default to 225 (Kenya standard)
    standard_hours = frappe.db.get_single_value(
        "HR Settings",  # Single DocType (only one record exists)
        "standard_hours_per_month"  # Field name
    ) or 225  # Default value if not configured
    
    # Calculate hourly rate
    # flt() ensures proper decimal handling and rounds to 2 places
    hourly_rate = flt(doc.base / standard_hours, 2)
    
    # Set the calculated value to the document
    # This will be saved automatically with the document
    doc.hourly_rate = hourly_rate


@frappe.whitelist()
def calculate_hourly_rate(salary_structure_assignment):
    """
    MANUAL CALCULATION: Called when user clicks "Calculate Hourly Rate" button.
    
    PURPOSE:
    Allow HR to manually recalculate hourly rate after changing salary.
    
    PARAMETERS:
    - salary_structure_assignment: Document name (ID) of the salary assignment
    
    PROCESS:
    1. Load the full document from database
    2. Call the automatic calculation function
    3. Save the document (persists the hourly rate)
    4. Show success message to user
    
    WHEN USED:
    - When HR updates salary mid-month
    - When fixing incorrect hourly rates
    - When standard hours change in HR Settings
    
    HOW TO CALL FROM UI:
    This is linked to a button in Salary Structure Assignment form.
    The @frappe.whitelist() decorator makes it callable from browser.
    """
    # Load the full document from database
    doc = frappe.get_doc("Salary Structure Assignment", salary_structure_assignment)
    
    # Calculate hourly rate using the same logic
    calculate_hourly_rate_on_save(doc, None)
    
    # Save the document to persist changes
    doc.save()
    
    # Show success message to user
    # _() is translation function for multi-language support
    frappe.msgprint(_("Hourly rate calculated: {0}").format(doc.hourly_rate))

