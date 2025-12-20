app_name = "vc_app"
app_title = "VC Overtime Management"
app_publisher = "Your Company"
app_description = "Simplified overtime management using Additional Salary"
app_icon = "octicon octicon-clock"
app_color = "blue"
app_email = "nidhin.regency@gmail.com"
app_license = "MIT"
app_version = "2.0.0"

required_apps = ["hrms"]

# Document Events
doc_events = {
    
    "Salary Structure Assignment": {
        "validate": "vc_app.vc_overtime.overtime_calculator.calculate_hourly_rate_on_save"
    },
    "Salary Slip": {
        "before_save": "vc_app.vc_overtime.doctype_hooks.salary_slip.before_save",
    }
}

# Installation
after_install = "vc_app.install.after_install"

# Fixtures for custom fields
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
                # ===== HR SETTINGS =====
                "HR Settings-overtime_section",
                "HR Settings-enable_overtime_tracking",
                "HR Settings-standard_hours_per_month",
                "HR Settings-weekday_overtime_multiplier",
                "HR Settings-holiday_overtime_multiplier",
                "HR Settings-sunday_overtime_multiplier",
                "HR Settings-overtime_variance_seconds",
                "HR Settings-overtime_components_section",
                "HR Settings-weekday_overtime_component",
                "HR Settings-holiday_overtime_component",
                
                # ===== EMPLOYEE =====
                "Employee-overtime_settings_section",
                "Employee-eligible_for_overtime",
                "Employee-overtime_notes",
                
                # ===== SALARY STRUCTURE ASSIGNMENT =====
                "Salary Structure Assignment-hourly_rate_section",
                "Salary Structure Assignment-hourly_rate",
                "Salary Structure Assignment-calculate_hourly_rate",
                
                # ===== EMPLOYEE CHECKIN =====
                "Employee Checkin-original_time",
                "Employee Checkin-is_overtime_processed",
                "Employee Checkin-overtime_reset_reason",
                
                # ===== ATTENDANCE =====
                "Attendance-overtime_tracking_section",
                "Attendance-calculated_overtime_hours",
                "Attendance-column_break_ot1",
                "Attendance-overtime_type",
                "Attendance-column_break_ot2",
                "Attendance-is_overtime_approved",
                "Attendance-overtime_additional_salary",
                "Attendance-audit_section",
                "Attendance-reset_close_time",
                "Attendance-effective_out_time",
                
                # ===== ADDITIONAL SALARY =====
                "Additional Salary-overtime_details_section",
                "Additional Salary-is_overtime_salary",
                "Additional Salary-overtime_attendance",
                "Additional Salary-overtime_hours",
                "Additional Salary-actual_worked_hours",
                "Additional Salary-overtime_column_break",
                "Additional Salary-overtime_type",
                "Additional Salary-overtime_calculation_method",
                "Additional Salary-comp_off_section",
                "Additional Salary-comp_off_granted",
                "Additional Salary-comp_off_days",
                "Additional Salary-comp_off_column_break",
                "Additional Salary-comp_off_leave_allocation",
                "Additional Salary-comp_off_leave_type",
                
                # ===== SHIFT TYPE (New Holiday/Sunday policies) =====
                "Shift Type-overtime_section",
                "Shift Type-overtime_allowance_minutes",
                "Shift Type-overtime_column_break",
                "Shift Type-overtime_calculation_info",
                "Shift Type-overtime_reset_info",
                "Shift Type-holiday_overtime_section",
                "Shift Type-holiday_overtime_calculation_type",
                "Shift Type-holiday_comp_off_leave_type",
                "Shift Type-holiday_min_hours_for_comp_off",
                "Shift Type-holiday_column_break",
                "Shift Type-holiday_policy_info",
                "Shift Type-sunday_overtime_section",
                "Shift Type-sunday_overtime_calculation_type",
                "Shift Type-sunday_comp_off_leave_type",
                "Shift Type-sunday_min_hours_for_comp_off",
                "Shift Type-sunday_column_break",
                "Shift Type-sunday_policy_info",
                
                # ===== LEAVE ALLOCATION (New Comp Off tracking) =====
                "Leave Allocation-overtime_comp_off_section",
                "Leave Allocation-is_overtime_comp_off",
                "Leave Allocation-overtime_additional_salary",
                "Leave Allocation-overtime_column_break",
                "Leave Allocation-overtime_work_date",
                "Leave Allocation-overtime_type",
                
                # ===== SALARY COMPONENT =====
                "Salary Component-overtime_component_section",
                "Salary Component-is_overtime_component",
                "Salary Component-overtime_multiplier_weekday",
                "Salary Component-overtime_multiplier_holiday",
            ]]
        ]
    }
]