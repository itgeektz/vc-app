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
                # HR Settings
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
                
                # Employee
                "Employee-overtime_settings_section",
                "Employee-eligible_for_overtime",
                "Employee-overtime_notes",
                
                # Salary Structure Assignment
                "Salary Structure Assignment-hourly_rate_section",
                "Salary Structure Assignment-hourly_rate",
                "Salary Structure Assignment-calculate_hourly_rate",
                
                # Employee Checkin
                "Employee Checkin-original_time",
                "Employee Checkin-is_overtime_processed",
                "Employee Checkin-overtime_reset_reason",
                
                # Attendance
                "Attendance-overtime_additional_salary",
                "Attendance-overtime_type",
                "Attendance-overtime_tracking_section",
                "Attendance-column_break_ot2",
                "Attendance-reset_close_time",
                "Attendance-effective_out_time",
                "Attendance-audit_section",
                "Attendance-column_break_ot1",
                "Attendance-overtime_additional_salary",
                "Attendance-overtime_type",
                "Attendance-overtime_tracking_section",
                "Attendance-column_break_ot2",
                "Attendance-reset_close_time",
                "Attendance-effective_out_time",
                "Attendance-audit_section",
                "Attendance-column_break_ot1",

                
                # Additional Salary
                "Additional Salary-is_overtime_salary",
                "Additional Salary-overtime_attendance",
                "Additional Salary-overtime_hours",
                "Additional Salary-overtime_type",
                "Additional Salary-overtime_details_section",

                #Shift Type
                "Shift Type-overtime_reset_info",
                "Shift Type-overtime_column_break",
                "Shift Type-overtime_calculation_info",
                "Shift Type-overtime_allowance_minutes",
                "Shift Type-overtime_section",

                #Salary Component

                "Salary Component-overtime_multiplier_holiday",
                "Salary Component-overtime_multiplier_weekday",
                "Salary Component-is_overtime_component",
                "Salary Component-overtime_component_section",


            ]]
        ]
    }
]
