import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """
    Run after app installation
    """
    print("="*60)
    print("Installing VC Overtime Management (Simplified)")
    print("="*60)
    
    create_overtime_custom_fields()
    create_salary_components()
    configure_hr_settings()
    
    frappe.db.commit()
    
    print("✓ Installation complete!")
    print("="*60)

def create_overtime_custom_fields():
    """
    Create all custom fields
    """
    custom_fields = {
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
                "fieldname": "overtime_type",
                "label": "Overtime Type",
                "fieldtype": "Select",
                "options": "\nNormal\nHoliday\nSunday",
                "insert_after": "calculated_overtime_hours",
                "read_only": 1
            },
            {
                "fieldname": "is_overtime_approved",
                "label": "Overtime Approved",
                "fieldtype": "Check",
                "insert_after": "overtime_type",
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
            }
        ],
        
        "Additional Salary": [
            {
                "fieldname": "is_overtime_salary",
                "label": "Is Overtime Salary",
                "fieldtype": "Check",
                "insert_after": "amount",
                "read_only": 1,
                "default": "0",
                "hidden": 1
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
                "fieldname": "overtime_type",
                "label": "Overtime Type",
                "fieldtype": "Select",
                "options": "\nNormal\nHoliday\nSunday",
                "insert_after": "overtime_hours",
                "read_only": 1,
                "depends_on": "eval:doc.is_overtime_salary==1"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    print("✓ Custom fields created")

def create_salary_components():
    """
    Create overtime salary components
    """
    components = [
        {
            "name": "Overtime Pay - Weekday",
            "abbr": "OT-WD",
            "type": "Earning",
            "description": "Overtime payment for normal weekdays (1.5x)"
        },
        {
            "name": "Overtime Pay - Holiday",
            "abbr": "OT-HOL",
            "type": "Earning",
            "description": "Overtime payment for holidays/Sundays (2.0x)"
        }
    ]
    
    for comp in components:
        if not frappe.db.exists("Salary Component", comp["name"]):
            doc = frappe.new_doc("Salary Component")
            doc.salary_component = comp["name"]
            doc.salary_component_abbr = comp["abbr"]
            doc.type = comp["type"]
            doc.description = comp["description"]
            doc.insert(ignore_permissions=True)
            print(f"✓ Created salary component: {comp['name']}")

def configure_hr_settings():
    """
    Configure HR Settings with default overtime values
    """
    hr_settings = frappe.get_single("HR Settings")
    
    if not hr_settings.get("enable_overtime_tracking"):
        hr_settings.enable_overtime_tracking = 1
        hr_settings.standard_hours_per_month = 225
        hr_settings.weekday_overtime_multiplier = 1.5
        hr_settings.holiday_overtime_multiplier = 2.0
        hr_settings.sunday_overtime_multiplier = 2.0
        hr_settings.overtime_variance_seconds = 3
        
        # Set salary components
        hr_settings.weekday_overtime_component = "Overtime Pay - Weekday"
        hr_settings.holiday_overtime_component = "Overtime Pay - Holiday"
        
        hr_settings.save(ignore_permissions=True)
        print("✓ HR Settings configured")
