# =====================================================================
# FILE: vc_app/vc_overtime/setup/install.py
# MERGED: Existing overtime + New Holiday/Sunday policies + Comp Off
# =====================================================================

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """
    Run after app installation
    Combines existing overtime setup + new Holiday/Sunday policies
    """
    print("\n" + "="*60)
    print("Installing VC Overtime Management")
    print("="*60 + "\n")
    
    try:
        # 1. Create all custom fields (existing + new)
        create_overtime_custom_fields()
        
        # 2. Create salary components
        create_salary_components()
        
        # 3. Create Compensatory Off leave type (NEW)
        create_comp_off_leave_type()
        
        # 4. Configure HR Settings
        configure_hr_settings()
        
        frappe.db.commit()
        
        # 5. Show success message
        print("\n" + "="*60)
        print("✓ VC Overtime Management installed successfully!")
        print("="*60 + "\n")
        print("Next steps:")
        print("1. Go to HR Settings and verify overtime configuration")
        print("2. Configure Holiday/Sunday policies in each Shift Type")
        print("3. Enable 'Eligible for Overtime' on Employee records")
        print("4. Access VC Overtime Report from: HR > Reports")
        print("\n")
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "VC Overtime Install Error")
        print(f"\n⚠️  Warning: Some setup steps failed: {str(e)}")
        print("Please check Error Log for details.\n")


def create_overtime_custom_fields():
    """
    Create ALL custom fields - existing + new Holiday/Sunday/CompOff fields
    """
    custom_fields = {
        # ===== HR SETTINGS (Existing) =====
        "HR Settings": [
            {
                "fieldname": "overtime_section",
                "label": "Overtime Configuration",
                "fieldtype": "Section Break",
                "insert_after": "leave_approval_notification_template",
                "collapsible": 1
            },
            {
                "fieldname": "enable_overtime_tracking",
                "label": "Enable Overtime Tracking",
                "fieldtype": "Check",
                "insert_after": "overtime_section",
                "default": "1"
            },
            {
                "fieldname": "standard_hours_per_month",
                "label": "Standard Hours per Month",
                "fieldtype": "Int",
                "insert_after": "enable_overtime_tracking",
                "default": "225",
                "description": "Used for hourly rate calculation (Kenya: 225)"
            },
            {
                "fieldname": "weekday_overtime_multiplier",
                "label": "Weekday Overtime Multiplier",
                "fieldtype": "Float",
                "insert_after": "standard_hours_per_month",
                "default": "1.5",
                "precision": "2"
            },
            {
                "fieldname": "holiday_overtime_multiplier",
                "label": "Holiday Overtime Multiplier",
                "fieldtype": "Float",
                "insert_after": "weekday_overtime_multiplier",
                "default": "2.0",
                "precision": "2"
            },
            {
                "fieldname": "sunday_overtime_multiplier",
                "label": "Sunday Overtime Multiplier",
                "fieldtype": "Float",
                "insert_after": "holiday_overtime_multiplier",
                "default": "2.0",
                "precision": "2"
            },
            {
                "fieldname": "overtime_variance_seconds",
                "label": "Overtime Variance Seconds (Non-Eligible)",
                "fieldtype": "Int",
                "insert_after": "sunday_overtime_multiplier",
                "default": "3",
                "description": "3-4 seconds variance for non-eligible employee reset"
            },
            {
                "fieldname": "overtime_components_section",
                "label": "Overtime Salary Components",
                "fieldtype": "Section Break",
                "insert_after": "overtime_variance_seconds"
            },
            {
                "fieldname": "weekday_overtime_component",
                "label": "Weekday Overtime Component",
                "fieldtype": "Link",
                "options": "Salary Component",
                "insert_after": "overtime_components_section"
            },
            {
                "fieldname": "holiday_overtime_component",
                "label": "Holiday/Sunday Overtime Component",
                "fieldtype": "Link",
                "options": "Salary Component",
                "insert_after": "weekday_overtime_component"
            }
        ],
        
        # ===== EMPLOYEE (Existing) =====
        "Employee": [
            {
                "fieldname": "overtime_settings_section",
                "label": "Overtime Settings",
                "fieldtype": "Section Break",
                "insert_after": "attendance_and_leave_details",
                "collapsible": 1
            },
            {
                "fieldname": "eligible_for_overtime",
                "label": "Eligible for Overtime",
                "fieldtype": "Check",
                "insert_after": "overtime_settings_section",
                "default": "0"
            },
            {
                "fieldname": "overtime_notes",
                "label": "Overtime Notes",
                "fieldtype": "Small Text",
                "insert_after": "eligible_for_overtime"
            }
        ],
        
        # ===== SALARY STRUCTURE ASSIGNMENT (Existing) =====
        "Salary Structure Assignment": [
            {
                "fieldname": "hourly_rate_section",
                "label": "Hourly Rate",
                "fieldtype": "Section Break",
                "insert_after": "base",
                "collapsible": 1
            },
            {
                "fieldname": "hourly_rate",
                "label": "Hourly Rate",
                "fieldtype": "Currency",
                "insert_after": "hourly_rate_section",
                "read_only": 1,
                "description": "Auto-calculated: Base / Standard Hours per Month"
            },
            {
                "fieldname": "calculate_hourly_rate",
                "label": "Calculate Hourly Rate",
                "fieldtype": "Button",
                "insert_after": "hourly_rate"
            }
        ],
        
        # ===== EMPLOYEE CHECKIN (Existing) =====
        "Employee Checkin": [
            {
                "fieldname": "original_time",
                "label": "Original Time",
                "fieldtype": "Datetime",
                "insert_after": "time",
                "read_only": 1,
                "hidden": 1
            },
            {
                "fieldname": "is_overtime_processed",
                "label": "Overtime Processed",
                "fieldtype": "Check",
                "insert_after": "original_time",
                "read_only": 1,
                "default": "0",
                "hidden": 1
            },
            {
                "fieldname": "overtime_reset_reason",
                "label": "Overtime Reset Reason",
                "fieldtype": "Small Text",
                "insert_after": "is_overtime_processed",
                "read_only": 1,
                "hidden": 1
            }
        ],
        
        # ===== ATTENDANCE (Existing) =====
        "Attendance": [
            {
                "fieldname": "overtime_tracking_section",
                "label": "Overtime Tracking",
                "fieldtype": "Section Break",
                "insert_after": "late_entry",
                "collapsible": 1
            },
            {
                "fieldname": "calculated_overtime_hours",
                "label": "Calculated Overtime Hours",
                "fieldtype": "Float",
                "insert_after": "overtime_tracking_section",
                "read_only": 1,
                "precision": "2"
            },
            {
                "fieldname": "column_break_ot1",
                "fieldtype": "Column Break",
                "insert_after": "calculated_overtime_hours"
            },
            {
                "fieldname": "overtime_type",
                "label": "Overtime Type",
                "fieldtype": "Select",
                "options": "\nNormal\nHoliday\nSunday",
                "insert_after": "column_break_ot1",
                "read_only": 1
            },
            {
                "fieldname": "column_break_ot2",
                "fieldtype": "Column Break",
                "insert_after": "overtime_type"
            },
            {
                "fieldname": "is_overtime_approved",
                "label": "Overtime Approved",
                "fieldtype": "Check",
                "insert_after": "column_break_ot2",
                "read_only": 1,
                "default": "0"
            },
            {
                "fieldname": "overtime_additional_salary",
                "label": "Overtime Additional Salary",
                "fieldtype": "Link",
                "options": "Additional Salary",
                "insert_after": "is_overtime_approved",
                "read_only": 1
            },
            {
                "fieldname": "audit_section",
                "label": "Time Audit",
                "fieldtype": "Section Break",
                "insert_after": "overtime_additional_salary",
                "collapsible": 1
            },
            {
                "fieldname": "reset_close_time",
                "label": "Reset Close Time",
                "fieldtype": "Datetime",
                "insert_after": "audit_section",
                "read_only": 1
            },
            {
                "fieldname": "effective_out_time",
                "label": "Effective Out Time",
                "fieldtype": "Datetime",
                "insert_after": "reset_close_time",
                "read_only": 1
            }
        ],
        
        # ===== ADDITIONAL SALARY (Existing + Enhanced) =====
        "Additional Salary": [
            {
                "fieldname": "overtime_details_section",
                "label": "Overtime Details",
                "fieldtype": "Section Break",
                "insert_after": "amount",
                "collapsible": 1
            },
            {
                "fieldname": "is_overtime_salary",
                "label": "Is Overtime Salary",
                "fieldtype": "Check",
                "insert_after": "overtime_details_section",
                "read_only": 1,
                "default": "0"
            },
            {
                "fieldname": "overtime_attendance",
                "label": "Overtime Attendance",
                "fieldtype": "Link",
                "options": "Attendance",
                "insert_after": "is_overtime_salary",
                "read_only": 1,
                "depends_on": "eval:doc.is_overtime_salary==1"
            },
            {
                "fieldname": "overtime_hours",
                "label": "Overtime Hours",
                "fieldtype": "Float",
                "insert_after": "overtime_attendance",
                "read_only": 1,
                "precision": "2",
                "depends_on": "eval:doc.is_overtime_salary==1"
            },
            {
                "fieldname": "actual_worked_hours",
                "label": "Total Hours Worked",
                "fieldtype": "Float",
                "insert_after": "overtime_hours",
                "precision": "2",
                "depends_on": "eval:doc.is_overtime_salary==1",
                "read_only": 1,
                "description": "Total hours worked on the day"
            },
            {
                "fieldname": "overtime_column_break",
                "fieldtype": "Column Break",
                "insert_after": "actual_worked_hours"
            },
            {
                "fieldname": "overtime_type",
                "label": "Overtime Type",
                "fieldtype": "Select",
                "options": "\nNormal\nHoliday\nSunday",
                "insert_after": "overtime_column_break",
                "read_only": 1,
                "depends_on": "eval:doc.is_overtime_salary==1"
            },
            {
                "fieldname": "overtime_calculation_method",
                "label": "Calculation Method",
                "fieldtype": "Select",
                "insert_after": "overtime_type",
                "options": "\nExtra Hours Only\nAll Hours as Overtime\nAll Hours + Comp Off\nExtra Hours + Comp Off",
                "depends_on": "eval:doc.is_overtime_salary==1",
                "read_only": 1,
                "description": "How the overtime was calculated"
            },
            {
                "fieldname": "comp_off_section",
                "label": "Compensatory Off",
                "fieldtype": "Section Break",
                "insert_after": "overtime_calculation_method",
                "depends_on": "eval:doc.is_overtime_salary==1",
                "collapsible": 1
            },
            {
                "fieldname": "comp_off_granted",
                "label": "Comp Off Granted",
                "fieldtype": "Check",
                "insert_after": "comp_off_section",
                "depends_on": "eval:doc.is_overtime_salary==1",
                "read_only": 1,
                "default": "0"
            },
            {
                "fieldname": "comp_off_days",
                "label": "Comp Off Days",
                "fieldtype": "Float",
                "insert_after": "comp_off_granted",
                "precision": "1",
                "depends_on": "eval:doc.comp_off_granted==1",
                "read_only": 1,
                "default": "1.0"
            },
            {
                "fieldname": "comp_off_column_break",
                "fieldtype": "Column Break",
                "insert_after": "comp_off_days"
            },
            {
                "fieldname": "comp_off_leave_allocation",
                "label": "Comp Off Leave Allocation",
                "fieldtype": "Link",
                "options": "Leave Allocation",
                "insert_after": "comp_off_column_break",
                "depends_on": "eval:doc.comp_off_granted==1",
                "read_only": 1
            },
            {
                "fieldname": "comp_off_leave_type",
                "label": "Comp Off Leave Type",
                "fieldtype": "Link",
                "options": "Leave Type",
                "insert_after": "comp_off_leave_allocation",
                "depends_on": "eval:doc.comp_off_granted==1",
                "read_only": 1
            }
        ],
        
        # ===== SHIFT TYPE (New - Holiday/Sunday policies) =====
        "Shift Type": [
            {
                "fieldname": "overtime_section",
                "label": "Overtime Settings",
                "fieldtype": "Section Break",
                "insert_after": "end_time",
                "collapsible": 0
            },
            {
                "fieldname": "overtime_allowance_minutes",
                "label": "Overtime Allowance (Minutes)",
                "fieldtype": "Int",
                "insert_after": "overtime_section",
                "default": "0",
                "description": "Grace period in minutes before overtime starts counting"
            },
            {
                "fieldname": "overtime_column_break",
                "fieldtype": "Column Break",
                "insert_after": "overtime_allowance_minutes"
            },
            {
                "fieldname": "overtime_calculation_info",
                "label": "",
                "fieldtype": "HTML",
                "insert_after": "overtime_column_break",
                "options": """
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px;">
                        <strong>📋 Overtime Formula:</strong><br>
                        <code>OT = (Worked - 8 hours - Allowance)</code>
                    </div>
                """
            },
            {
                "fieldname": "overtime_reset_info",
                "label": "",
                "fieldtype": "HTML",
                "insert_after": "overtime_calculation_info",
                "options": """
                    <div style="background-color: #fff3e0; padding: 10px; border-radius: 5px;">
                        <strong>Reset:</strong> Check-in + 8h + Allowance + 3-4s
                    </div>
                """
            },
            {
                "fieldname": "holiday_overtime_section",
                "label": "Holiday Overtime Policy",
                "fieldtype": "Section Break",
                "insert_after": "overtime_reset_info",
                "collapsible": 1
            },
            {
                "fieldname": "holiday_overtime_calculation_type",
                "label": "Holiday Overtime Calculation",
                "fieldtype": "Select",
                "options": "\nExtra Hours Only\nAll Hours as Overtime\nAll Hours + Comp Off\nExtra Hours + Comp Off",
                "default": "Extra Hours Only",
                "insert_after": "holiday_overtime_section",
                "description": "How to calculate OT on public holidays"
            },
            {
                "fieldname": "holiday_comp_off_leave_type",
                "label": "Holiday Comp Off Leave Type",
                "fieldtype": "Link",
                "options": "Leave Type",
                "insert_after": "holiday_overtime_calculation_type",
                "depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.holiday_overtime_calculation_type)",
                "mandatory_depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.holiday_overtime_calculation_type)"
            },
            {
                "fieldname": "holiday_min_hours_for_comp_off",
                "label": "Min Hours for Holiday Comp Off",
                "fieldtype": "Float",
                "insert_after": "holiday_comp_off_leave_type",
                "default": "6.0",
                "precision": "1",
                "depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.holiday_overtime_calculation_type)"
            },
            {
                "fieldname": "holiday_column_break",
                "fieldtype": "Column Break",
                "insert_after": "holiday_min_hours_for_comp_off"
            },
            {
                "fieldname": "holiday_policy_info",
                "label": "",
                "fieldtype": "HTML",
                "insert_after": "holiday_column_break",
                "options": """
                    <div style="background-color: #fff3e0; padding: 10px; border-radius: 5px;">
                        <strong>🎉 Holiday Options:</strong><br>
                        <small>
                        • Extra Hours Only<br>
                        • All Hours as OT<br>
                        • All Hours + 1 Day Off<br>
                        • Extra Hours + 1 Day Off
                        </small>
                    </div>
                """
            },
            {
                "fieldname": "sunday_overtime_section",
                "label": "Sunday Overtime Policy",
                "fieldtype": "Section Break",
                "insert_after": "holiday_policy_info",
                "collapsible": 1
            },
            {
                "fieldname": "sunday_overtime_calculation_type",
                "label": "Sunday Overtime Calculation",
                "fieldtype": "Select",
                "options": "\nExtra Hours Only\nAll Hours as Overtime\nAll Hours + Comp Off\nExtra Hours + Comp Off",
                "default": "Extra Hours Only",
                "insert_after": "sunday_overtime_section"
            },
            {
                "fieldname": "sunday_comp_off_leave_type",
                "label": "Sunday Comp Off Leave Type",
                "fieldtype": "Link",
                "options": "Leave Type",
                "insert_after": "sunday_overtime_calculation_type",
                "depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.sunday_overtime_calculation_type)",
                "mandatory_depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.sunday_overtime_calculation_type)"
            },
            {
                "fieldname": "sunday_min_hours_for_comp_off",
                "label": "Min Hours for Sunday Comp Off",
                "fieldtype": "Float",
                "insert_after": "sunday_comp_off_leave_type",
                "default": "6.0",
                "precision": "1",
                "depends_on": "eval:['All Hours + Comp Off', 'Extra Hours + Comp Off'].includes(doc.sunday_overtime_calculation_type)"
            },
            {
                "fieldname": "sunday_column_break",
                "fieldtype": "Column Break",
                "insert_after": "sunday_min_hours_for_comp_off"
            },
            {
                "fieldname": "sunday_policy_info",
                "label": "",
                "fieldtype": "HTML",
                "insert_after": "sunday_column_break",
                "options": """
                    <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px;">
                        <strong>📅 Sunday Options:</strong><br>
                        <small>
                        • Extra Hours Only<br>
                        • All Hours as OT<br>
                        • All Hours + 1 Day Off<br>
                        • Extra Hours + 1 Day Off
                        </small>
                    </div>
                """
            }
        ],
        
        # ===== LEAVE ALLOCATION (New - Comp Off tracking) =====
        "Leave Allocation": [
            {
                "fieldname": "overtime_comp_off_section",
                "label": "Overtime Compensatory Off",
                "fieldtype": "Section Break",
                "insert_after": "leave_type",
                "collapsible": 1
            },
            {
                "fieldname": "is_overtime_comp_off",
                "label": "Is Overtime Comp Off",
                "fieldtype": "Check",
                "insert_after": "overtime_comp_off_section",
                "read_only": 1,
                "default": "0"
            },
            {
                "fieldname": "overtime_additional_salary",
                "label": "Related Overtime Salary",
                "fieldtype": "Link",
                "options": "Additional Salary",
                "insert_after": "is_overtime_comp_off",
                "depends_on": "eval:doc.is_overtime_comp_off==1",
                "read_only": 1
            },
            {
                "fieldname": "overtime_column_break",
                "fieldtype": "Column Break",
                "insert_after": "overtime_additional_salary"
            },
            {
                "fieldname": "overtime_work_date",
                "label": "Overtime Work Date",
                "fieldtype": "Date",
                "insert_after": "overtime_column_break",
                "depends_on": "eval:doc.is_overtime_comp_off==1",
                "read_only": 1
            },
            {
                "fieldname": "overtime_type",
                "label": "Overtime Type",
                "fieldtype": "Select",
                "insert_after": "overtime_work_date",
                "options": "\nHoliday\nSunday",
                "depends_on": "eval:doc.is_overtime_comp_off==1",
                "read_only": 1
            }
        ],
        
        # ===== SALARY COMPONENT (For multipliers) =====
        "Salary Component": [
            {
                "fieldname": "overtime_component_section",
                "label": "Overtime Component Settings",
                "fieldtype": "Section Break",
                "insert_after": "description",
                "collapsible": 1
            },
            {
                "fieldname": "is_overtime_component",
                "label": "Is Overtime Component",
                "fieldtype": "Check",
                "insert_after": "overtime_component_section",
                "default": "0"
            },
            {
                "fieldname": "overtime_multiplier_weekday",
                "label": "Weekday Multiplier",
                "fieldtype": "Float",
                "insert_after": "is_overtime_component",
                "depends_on": "eval:doc.is_overtime_component==1",
                "precision": "2",
                "default": "1.5"
            },
            {
                "fieldname": "overtime_multiplier_holiday",
                "label": "Holiday/Sunday Multiplier",
                "fieldtype": "Float",
                "insert_after": "overtime_multiplier_weekday",
                "depends_on": "eval:doc.is_overtime_component==1",
                "precision": "2",
                "default": "2.0"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
    
    print("✓ Custom fields created successfully")
    print("  - HR Settings: Overtime configuration")
    print("  - Employee: Overtime eligibility")
    print("  - Shift Type: Holiday/Sunday policies with comp off")
    print("  - Additional Salary: Enhanced overtime tracking")
    print("  - Leave Allocation: Comp off linking")
    print("  - Attendance: Overtime tracking fields")
    print("  - Employee Checkin: Audit fields")
    print("  - Salary Structure Assignment: Hourly rate")
    print("  - Salary Component: Overtime multipliers")


def create_salary_components():
    """
    Create overtime salary components
    """
    components = [
        {
            "name": "Overtime Pay - Weekday",
            "abbr": "OT-WD",
            "type": "Earning",
            "description": "Overtime payment for normal weekdays (1.5x)",
            "is_overtime": 1,
            "multiplier_weekday": 1.5,
            "multiplier_holiday": 1.5
        },
        {
            "name": "Overtime Pay - Holiday",
            "abbr": "OT-HOL",
            "type": "Earning",
            "description": "Overtime payment for holidays/Sundays (2.0x)",
            "is_overtime": 1,
            "multiplier_weekday": 2.0,
            "multiplier_holiday": 2.0
        }
    ]
    
    for comp in components:
        if not frappe.db.exists("Salary Component", comp["name"]):
            doc = frappe.new_doc("Salary Component")
            doc.salary_component = comp["name"]
            doc.salary_component_abbr = comp["abbr"]
            doc.type = comp["type"]
            doc.description = comp["description"]
            doc.is_overtime_component = comp["is_overtime"]
            doc.overtime_multiplier_weekday = comp["multiplier_weekday"]
            doc.overtime_multiplier_holiday = comp["multiplier_holiday"]
            doc.insert(ignore_permissions=True)
            print(f"✓ Created salary component: {comp['name']}")
        else:
            print(f"✓ Salary component exists: {comp['name']}")


def create_comp_off_leave_type():
    """
    Create Compensatory Off leave type
    """
    leave_type_name = "Compensatory Off"
    
    if frappe.db.exists("Leave Type", leave_type_name):
        print(f"✓ Leave Type '{leave_type_name}' already exists")
        return
    
    try:
        leave_type = frappe.new_doc("Leave Type")
        leave_type.leave_type_name = leave_type_name
        leave_type.max_leaves_allowed = 0  # Unlimited (earned)
        leave_type.is_earned_leave = 1
        leave_type.is_compensatory = 1
        leave_type.allow_negative = 0
        leave_type.include_holiday = 1
        leave_type.is_carry_forward = 1
        leave_type.max_carry_forwarded_leaves = 90
        leave_type.expire_carry_forwarded_leaves_after_days = 90
        leave_type.earned_leave_frequency = "Monthly"
        leave_type.rounding = 0.5
        
        leave_type.insert(ignore_permissions=True)
        
        print(f"✓ Created Leave Type: {leave_type_name}")
        print(f"  - Valid for: 90 days")
        print(f"  - Max carry forward: 90 days")
        
    except Exception as e:
        print(f"⚠️  Could not create Leave Type: {str(e)}")


def configure_hr_settings():
    """
    Configure HR Settings with overtime defaults
    """
    try:
        hr_settings = frappe.get_single("HR Settings")
        
        updated = False
        
        # Enable overtime tracking
        if not hr_settings.get("enable_overtime_tracking"):
            hr_settings.enable_overtime_tracking = 1
            updated = True
        
        # Set standard hours
        if not hr_settings.get("standard_hours_per_month"):
            hr_settings.standard_hours_per_month = 225
            updated = True
        
        # Set multipliers
        if not hr_settings.get("weekday_overtime_multiplier"):
            hr_settings.weekday_overtime_multiplier = 1.5
            updated = True
            print("✓ Set weekday multiplier: 1.5x")
        
        if not hr_settings.get("holiday_overtime_multiplier"):
            hr_settings.holiday_overtime_multiplier = 2.0
            updated = True
            print("✓ Set holiday multiplier: 2.0x")
        
        if not hr_settings.get("sunday_overtime_multiplier"):
            hr_settings.sunday_overtime_multiplier = 2.0
            updated = True
            print("✓ Set Sunday multiplier: 2.0x")
        
        if not hr_settings.get("overtime_variance_seconds"):
            hr_settings.overtime_variance_seconds = 3
            updated = True
        
        # Set salary components
        if not hr_settings.get("weekday_overtime_component"):
            hr_settings.weekday_overtime_component = "Overtime Pay - Weekday"
            updated = True
        
        if not hr_settings.get("holiday_overtime_component"):
            hr_settings.holiday_overtime_component = "Overtime Pay - Holiday"
            updated = True
        
        if updated:
            hr_settings.flags.ignore_mandatory = True
            hr_settings.save(ignore_permissions=True)
            print("✓ HR Settings configured")
        else:
            print("✓ HR Settings already configured")
            
    except Exception as e:
        print(f"⚠️  Could not update HR Settings: {str(e)}")


def validate_setup():
    """
    Validate installation
    Can be called manually: bench console > from vc_app.vc_overtime.setup.install import validate_setup; validate_setup()
    """
    print("\n" + "="*60)
    print("Validating VC Overtime Setup")
    print("="*60 + "\n")
    
    issues = []
    
    # Check custom fields
    required_fields = {
        "Shift Type": ["overtime_allowance_minutes", "holiday_overtime_calculation_type"],
        "Additional Salary": ["is_overtime_salary", "comp_off_granted"],
        "Leave Allocation": ["is_overtime_comp_off", "overtime_work_date"],
        "Employee": ["eligible_for_overtime"],
        "HR Settings": ["enable_overtime_tracking", "weekday_overtime_multiplier"]
    }
    
    for doctype, fields in required_fields.items():
        for field in fields:
            if not frappe.db.exists("Custom Field", f"{doctype}-{field}"):
                issues.append(f"Missing: {doctype}.{field}")
    
    # Check Leave Type
    if not frappe.db.exists("Leave Type", "Compensatory Off"):
        issues.append("Missing: Compensatory Off Leave Type")
    
    # Check Salary Components
    if not frappe.db.exists("Salary Component", "Overtime Pay - Weekday"):
        issues.append("Missing: Overtime Pay - Weekday")
    if not frappe.db.exists("Salary Component", "Overtime Pay - Holiday"):
        issues.append("Missing: Overtime Pay - Holiday")
    
    if issues:
        print("⚠️  Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ All validations passed!")
        print("\nSetup is complete and ready to use.")
        return True