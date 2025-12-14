// =====================================================================
// FILE: vc_app/vc_overtime/report/vc_overtime_report/vc_overtime_report.js
// WORKING SOLUTION - Enables checkboxes after render
// =====================================================================

frappe.query_reports["VC Overtime Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "department",
            "label": __("Department"),
            "fieldtype": "Link",
            "options": "Department"
        },
        {
            "fieldname": "eligible_for_overtime",
            "label": __("Eligible for Overtime"),
            "fieldtype": "Select",
            "options": ["", "Yes", "No"]
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Format eligibility
        if (column.fieldname == "is_eligible") {
            if (data.is_eligible == 0) {
                value = '<span style="color: red; font-weight: bold;">✗ No</span>';
            } else {
                value = '<span style="color: green; font-weight: bold;">✓ Yes</span>';
            }
        }
        
        // Format status with colors
        if (column.fieldname == "status") {
            if (data.status == "Approved & Paid") {
                value = `<span style="color: green; font-weight: bold;">✓ ${data.status}</span>`;
            } else if (data.status == "Pending Review") {
                value = `<span style="color: orange; font-weight: bold;">⏳ ${data.status}</span>`;
            } else if (data.status == "No Overtime") {
                value = `<span style="color: gray;">${data.status}</span>`;
            }
        }
        
        // Highlight special overtime types
        if (column.fieldname == "overtime_type") {
            if (data.overtime_type == "Holiday") {
                value = `<span style="color: red; font-weight: bold;">🎉 Holiday</span>`;
            } else if (data.overtime_type == "Sunday") {
                value = `<span style="color: blue; font-weight: bold;">📅 Sunday</span>`;
            } else if (data.overtime_type == "Normal") {
                value = `<span>Normal</span>`;
            }
        }
        
        // Format currency with bold
        if (column.fieldname == "overtime_amount" && data.overtime_amount > 0) {
            value = `<span style="font-weight: bold; color: #2e7d32;">KES ${parseFloat(data.overtime_amount).toLocaleString('en-KE', {minimumFractionDigits: 2})}</span>`;
        }
        
        return value;
    },
    
    onload: function(report) {
        // Initialize checked items array
        report.checked_items = [];
        
        // Add buttons to Actions menu
        report.page.add_inner_button(__("Approve Selected"), function() {
            process_selected_overtime(report, "approve");
        }, __("Actions"));
        
        report.page.add_inner_button(__("Reject & Reset Times"), function() {
            process_selected_overtime(report, "reject");
        }, __("Actions"));
        
        report.page.add_inner_button(__("Show Summary"), function() {
            show_overtime_summary(report);
        }, __("View"));
        
        report.page.add_inner_button(__("Refresh Data"), function() {
            report.refresh();
        }, __("View"));
        
        // Enable checkboxes after report renders
        setTimeout(() => {
            enable_checkboxes(report);
        }, 500);
    },
    
    // Enable checkboxes
    get_datatable_options(options) {
        return Object.assign(options, {
            checkboxColumn: true,
            events: {
                onCheckRow: function(data) {
                    console.log("Row checked/unchecked");
                }
            },
            cellHeight: 35,
            inlineFilters: true
        });
    }
};

// =====================================================================
// ENABLE CHECKBOXES FUNCTION
// =====================================================================

function enable_checkboxes(report) {
    console.log("Enabling checkboxes...");
    
    // Find all disabled checkboxes in the report
    let $checkboxes = $('.dt-cell__content input[type="checkbox"][disabled]');
    
    console.log("Found disabled checkboxes:", $checkboxes.length);
    
    // Enable them and add click handler
    $checkboxes.each(function(index) {
        let $checkbox = $(this);
        
        // Remove disabled attribute
        $checkbox.removeAttr('disabled');
        $checkbox.removeClass('disabled-deselected');
        
        // Add click handler
        $checkbox.off('click').on('click', function(e) {
            let is_checked = $(this).is(':checked');
            
            // Find the row index
            let $cell = $(this).closest('.dt-cell');
            let $row = $cell.closest('.dt-row');
            let row_index = $row.index();
            
            console.log("Checkbox clicked, row:", row_index, "checked:", is_checked);
            
            // Get row data
            if (report.data && report.data[row_index]) {
                let row_data = report.data[row_index];
                
                // Initialize checked_items if needed
                if (!report.checked_items) {
                    report.checked_items = [];
                }
                
                if (is_checked) {
                    // Add to checked items
                    let exists = report.checked_items.find(item => 
                        item.attendance === row_data.attendance
                    );
                    
                    if (!exists) {
                        report.checked_items.push(row_data);
                        console.log("Added to checked items:", row_data.attendance);
                    }
                } else {
                    // Remove from checked items
                    report.checked_items = report.checked_items.filter(item => 
                        item.attendance !== row_data.attendance
                    );
                    console.log("Removed from checked items:", row_data.attendance);
                }
                
                console.log("Total checked:", report.checked_items.length);
            }
        });
    });
    
    console.log("Checkboxes enabled!");
}

// =====================================================================
// MAIN PROCESSING FUNCTION
// =====================================================================

function process_selected_overtime(report, action) {
    // Get checked items from stored array
    let checked_data = report.checked_items || [];
    
    console.log("Processing checked data:", checked_data);
    
    if (!checked_data || checked_data.length === 0) {
        frappe.msgprint({
            title: __("No Selection"),
            message: __("Please select at least one record using the checkboxes in the first column"),
            indicator: "orange"
        });
        return;
    }
    
    // Show appropriate dialog based on action
    if (action === "approve") {
        show_approval_dialog(report, checked_data);
    } else if (action === "reject") {
        show_rejection_dialog(report, checked_data);
    }
}

// =====================================================================
// APPROVAL DIALOG
// =====================================================================

function show_approval_dialog(report, checked_data) {
    // Filter only eligible employees
    let eligible = checked_data.filter(row => row.is_eligible == 1 || row.is_eligible == "1");
    let non_eligible = checked_data.filter(row => row.is_eligible == 0 || row.is_eligible == "0");
    
    if (eligible.length === 0) {
        frappe.msgprint({
            title: __("No Eligible Employees"),
            message: __("None of the selected employees are eligible for overtime"),
            indicator: "red"
        });
        return;
    }
    
    let d = new frappe.ui.Dialog({
        title: __("Approve Overtime"),
        fields: [
            {
                fieldname: "summary_html",
                fieldtype: "HTML",
                options: get_approval_summary(eligible, non_eligible)
            }
        ],
        size: "large",
        primary_action_label: __("Approve & Create Additional Salary"),
        primary_action: function(values) {
            // Only process eligible employees
            let attendance_list = eligible.map(row => row.attendance);
            
            frappe.call({
                method: "vc_app.vc_overtime.overtime_processor.process_selected_overtime",
                args: {
                    attendance_list: attendance_list,
                    action: "approve"
                },
                freeze: true,
                freeze_message: __("Creating Additional Salary entries..."),
                callback: function(r) {
                    if (r.message) {
                        let result = r.message;
                        
                        // Show detailed results
                        if (result.errors && result.errors.length > 0) {
                            frappe.msgprint({
                                title: __("Processing Complete with Errors"),
                                message: __("Processed: {0}<br>Approved: {1}<br>Errors: {2}<br><br>Error Details:<br>{3}", 
                                    [result.processed, result.approved, result.errors.length, result.errors.join("<br>")]),
                                indicator: "orange"
                            });
                        } else {
                            frappe.show_alert({
                                message: __("✓ Successfully approved {0} overtime records", [result.approved]),
                                indicator: "green"
                            }, 5);
                        }
                        
                        // Clear checked items
                        report.checked_items = [];
                        report.refresh();
                        d.hide();
                    }
                },
                error: function(r) {
                    frappe.msgprint({
                        title: __("Error"),
                        message: __("Error processing overtime. Please check the error log."),
                        indicator: "red"
                    });
                }
            });
        }
    });
    
    d.show();
}

// =====================================================================
// REJECTION DIALOG
// =====================================================================

function show_rejection_dialog(report, checked_data) {
    let d = new frappe.ui.Dialog({
        title: __("Reject Overtime & Reset Times"),
        fields: [
            {
                fieldname: "warning_html",
                fieldtype: "HTML",
                options: get_rejection_warning(checked_data)
            }
        ],
        size: "large",
        primary_action_label: __("Yes, Reset Checkout Times"),
        primary_action: function(values) {
            let attendance_list = checked_data.map(row => row.attendance);
            
            frappe.call({
                method: "vc_app.vc_overtime.overtime_processor.process_selected_overtime",
                args: {
                    attendance_list: attendance_list,
                    action: "reject"
                },
                freeze: true,
                freeze_message: __("Resetting checkout times..."),
                callback: function(r) {
                    if (r.message) {
                        let result = r.message;
                        
                        // Show detailed results
                        if (result.errors && result.errors.length > 0) {
                            frappe.msgprint({
                                title: __("Processing Complete with Errors"),
                                message: __("Processed: {0}<br>Rejected: {1}<br>Errors: {2}<br><br>Error Details:<br>{3}", 
                                    [result.processed, result.rejected, result.errors.length, result.errors.join("<br>")]),
                                indicator: "orange"
                            });
                        } else {
                            frappe.show_alert({
                                message: __("✓ Successfully reset {0} checkout times", [result.rejected]),
                                indicator: "blue"
                            }, 5);
                        }
                        
                        // Clear checked items
                        report.checked_items = [];
                        report.refresh();
                        d.hide();
                    }
                },
                error: function(r) {
                    frappe.msgprint({
                        title: __("Error"),
                        message: __("Error resetting times. Please check the error log."),
                        indicator: "red"
                    });
                }
            });
        },
        secondary_action_label: __("Cancel")
    });
    
    d.show();
}

// =====================================================================
// SUMMARY GENERATORS
// =====================================================================

function get_approval_summary(eligible, non_eligible) {
    let total_hours = 0;
    let total_amount = 0;
    
    eligible.forEach(row => {
        total_hours += parseFloat(row.overtime_hours) || 0;
        total_amount += parseFloat(row.overtime_amount) || 0;
    });
    
    let html = `
        <div style="padding: 20px;">
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #2e7d32;">✓ Approval Summary</h4>
                <table class="table table-bordered" style="margin-top: 15px; background: white;">
                    <tr>
                        <td style="width: 60%; padding: 10px;"><strong>Eligible Employees:</strong></td>
                        <td style="padding: 10px; color: green; font-weight: bold; font-size: 16px;">${eligible.length}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 10px;"><strong>Total OT Hours:</strong></td>
                        <td style="padding: 10px; font-weight: bold;">${total_hours.toFixed(2)} hours</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;"><strong>Total OT Amount:</strong></td>
                        <td style="padding: 10px; color: green; font-weight: bold; font-size: 20px;">
                            KES ${total_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}
                        </td>
                    </tr>
                </table>
            </div>`;
    
    if (non_eligible.length > 0) {
        html += `
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                <strong>⚠️ Warning:</strong> ${non_eligible.length} selected employee(s) are NOT eligible for overtime and will be skipped.
            </div>`;
    }
    
    html += `
        <div style="border-left: 4px solid #2196F3; padding-left: 15px; margin-top: 20px;">
            <p style="margin: 0;"><strong>What will happen:</strong></p>
            <ul style="margin-top: 10px; margin-bottom: 0;">
                <li>✓ Create <strong>${eligible.length}</strong> Additional Salary entries</li>
                <li>✓ Link to respective attendance records</li>
                <li>✓ Mark as approved for payroll</li>
                <li>✓ Include in next salary slip generation</li>
            </ul>
        </div>
    </div>`;
    
    return html;
}

function get_rejection_warning(checked_data) {
    let html = `
        <div style="padding: 20px;">
            <div style="background-color: #ffebee; padding: 20px; border-radius: 5px; border-left: 4px solid #f44336; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #c62828;">⚠️ Warning: This action will reset checkout times</h4>
                <p style="margin-bottom: 0;"><strong>${checked_data.length}</strong> employee checkout times will be reset to shift end time (with 3-4 second variance).</p>
            </div>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p style="margin: 0;"><strong>What will happen:</strong></p>
                <ul style="margin-top: 10px; margin-bottom: 0;">
                    <li>🔄 Checkout times will be reset to shift end + variance (3-4 seconds)</li>
                    <li>📝 Original times will be stored for audit trail</li>
                    <li>❌ Overtime will be removed/recalculated</li>
                    <li>🔒 Cannot be undone automatically</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background-color: #e3f2fd; border-radius: 5px;">
                <p style="margin: 0; color: #1565c0;"><strong>ℹ️ Note:</strong> This is typically used for employees who are NOT eligible for overtime but worked extra hours.</p>
            </div>
        </div>`;
    
    return html;
}

// =====================================================================
// SUMMARY DIALOG
// =====================================================================

function show_overtime_summary(report) {
    let data = report.data || [];
    
    let total_records = data.length;
    let total_hours = 0;
    let total_amount = 0;
    let pending_count = 0;
    let approved_count = 0;
    let eligible_count = 0;
    let non_eligible_count = 0;
    
    // Process unique records only
    let processed_attendance = new Set();
    
    data.forEach(row => {
        // Skip if already processed (avoid duplicates)
        if (processed_attendance.has(row.attendance)) {
            return;
        }
        processed_attendance.add(row.attendance);
        
        total_hours += parseFloat(row.overtime_hours) || 0;
        total_amount += parseFloat(row.overtime_amount) || 0;
        
        if (row.status == "Approved & Paid") {
            approved_count++;
        } else if (row.status == "Pending Review") {
            pending_count++;
        }
        
        if (row.is_eligible == 1 || row.is_eligible == "1") {
            eligible_count++;
        } else {
            non_eligible_count++;
        }
    });
    
    let d = new frappe.ui.Dialog({
        title: __("Overtime Summary Report"),
        fields: [
            {
                fieldname: "summary_html",
                fieldtype: "HTML",
                options: `
                    <div style="padding: 20px;">
                        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                            <h3 style="margin-top: 0; color: #1565c0;">📊 Period Overview</h3>
                            <table class="table table-bordered" style="background: white;">
                                <tr style="background-color: #f5f5f5;">
                                    <td style="width: 60%; padding: 12px;"><strong>Total Records:</strong></td>
                                    <td style="padding: 12px; font-weight: bold; font-size: 18px;">${total_records}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px;"><strong>Total OT Hours:</strong></td>
                                    <td style="padding: 12px; font-weight: bold; font-size: 18px; color: #1976d2;">${total_hours.toFixed(2)} hours</td>
                                </tr>
                                <tr style="background-color: #e8f5e9;">
                                    <td style="padding: 12px;"><strong>Total OT Amount:</strong></td>
                                    <td style="padding: 12px; color: #2e7d32; font-weight: bold; font-size: 22px;">
                                        KES ${total_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}
                                    </td>
                                </tr>
                            </table>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                            <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px;">
                                <h4 style="margin-top: 0; color: #e65100;">👥 By Eligibility</h4>
                                <table class="table table-bordered" style="background: white;">
                                    <tr>
                                        <td style="padding: 8px;"><strong>Eligible:</strong></td>
                                        <td style="padding: 8px; color: green; font-weight: bold;">${eligible_count}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px;"><strong>Non-Eligible:</strong></td>
                                        <td style="padding: 8px; color: red; font-weight: bold;">${non_eligible_count}</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px;">
                                <h4 style="margin-top: 0; color: #6a1b9a;">📋 By Status</h4>
                                <table class="table table-bordered" style="background: white;">
                                    <tr>
                                        <td style="padding: 8px;"><strong>Pending:</strong></td>
                                        <td style="padding: 8px; color: orange; font-weight: bold;">${pending_count}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px;"><strong>Approved:</strong></td>
                                        <td style="padding: 8px; color: green; font-weight: bold;">${approved_count}</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                        
                        ${pending_count > 0 ? `
                        <div style="background-color: #fff9c4; padding: 15px; border-radius: 8px; border-left: 4px solid #fbc02d;">
                            <p style="margin: 0;"><strong>💡 Action Required:</strong> ${pending_count} overtime record(s) are pending review and approval.</p>
                        </div>
                        ` : ''}
                    </div>
                `
            }
        ],
        size: "large"
    });
    
    d.show();
}