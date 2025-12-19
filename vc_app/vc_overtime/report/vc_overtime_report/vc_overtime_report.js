// =====================================================================
// FILE: vc_app/vc_overtime/report/vc_overtime_report/vc_overtime_report.js
// FIXED VERSION: Corrected column index (visual column 10 for approved_overtime_hours)
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
        return value;
    },
    
    onload: function(report) {
        // Initialize storage
        report.edited_values = {};
        
        // Add buttons
        // In onload function, add this button:
        // Replace your "Refresh Display" button with this enhanced version:

        // Replace "Refresh Display" button with this:

        report.page.add_inner_button(__("Refresh Display"), async function() {
            // 1. Refresh the report data
            report.refresh();
            
            // 2. Wait for data to load, then apply stored edits
            setTimeout(async () => {
                try {
                    await applyStoredEdits();
                    frappe.show_alert({
                        message: "✓ Display refreshed with edits",
                        indicator: "green"
                    }, 3);
                } catch (err) {
                    console.error("Error applying edits:", err);
                }
            }, 500);
        }, );

        report.page.add_inner_button(__("Approve Selected"), function() {
            process_selected_overtime(report, "approve");
        }, __("Actions"));
        
        report.page.add_inner_button(__("Reject & Reset Times"), function() {
            process_selected_overtime(report, "reject");
        }, __("Actions"));

        report.page.add_inner_button(__("Clear All Edits"), async function() {
            await OvertimeEditCache.clearAll();
            report.refresh();
        }, __("Actions"));
        
        report.page.add_inner_button(__("Show Summary"), function() {
            show_overtime_summary(report);
        }, __("View"));

        report.page.add_inner_button(__("Show Pending Edits"), async function() {
            const edits = await OvertimeEditCache.getAll();
            frappe.show_alert(`${Object.keys(edits).length} pending edits`, "blue", 5);
            console.table(edits);
        }, __("View"));

        report.page.add_inner_button(__("Refresh Data"), function() {
            report.refresh();
        }, __("View"));
        setTimeout(async () => {
            const edits = await OvertimeEditCache.getAll();
            const count = Object.keys(edits).length;
            if (count > 0) {
                frappe.show_alert(`📝 ${count} pending edits`, "blue", 5);
            }
        }, 2000);
    
    },

    after_refresh: function (report) {
        if (report.datatable) {
            enable_manual_cell_editing(report);
        }
    },
    
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
// MANUAL CELL EDITING - COLUMN INDEX FIXED
// =====================================================================

function enable_manual_cell_editing(report) {

    console.log("=== ENABLING MANUAL CELL EDITING ===");

    // CRITICAL FIX: DataTable renders columns with an offset due to checkbox column
    // approved_overtime_hours is at index 8 in columns array, but visual column 10
    const VISUAL_COL_INDEX = 10; // Hardcoded correct visual column

    const $report_container = $(report.page.wrapper);

    const cell_selector =
        `.dt-cell--col-${VISUAL_COL_INDEX}:not([data-is-header]):not([data-is-filter]) .dt-cell__content`;

    console.log(`Attaching to column ${VISUAL_COL_INDEX} with selector: ${cell_selector}`);

    // Remove old handler
    $report_container.off('dblclick.manual-edit', cell_selector);

    // Attach handler
    $report_container.on(
        'dblclick.manual-edit',
        cell_selector,
        function (e) {

            console.log("🖱️ DOUBLE-CLICK DETECTED");

            e.stopPropagation();
            e.preventDefault();

            const $content = $(this);
            const $row = $content.closest('.dt-row');
            const row_index = $row.data('row-index');

            console.log("Row index:", row_index);

            // Ignore invalid & total row
            if (
                row_index === undefined ||
                row_index === 'totalRow' ||
                !report.data[row_index]
            ) {
                console.warn("Invalid row");
                return;
            }

            const row_data = report.data[row_index];
            console.log("Row data:", row_data);

            // Guard approved rows
            if (row_data.status === "Approved" || row_data.status === "Approved & Paid") {
                console.warn("Already approved");
                frappe.show_alert({
                    message: __("Cannot edit approved records"),
                    indicator: "red"
                }, 3);
                return;
            }

            // Already editing?
            if ($content.find('input').length) {
                console.log("Already editing");
                return;
            }

            const current_value =
                row_data.approved_overtime_hours ??
                row_data.overtime_hours ?? 0;

            console.log("Current value:", current_value);

            const $input = $('<input>', {
                type: 'text',
                value: current_value,
                placeholder: '0.00'
            }).css({
                width: '100%',
                padding: '4px',
                textAlign: 'right',
                border: '2px solid #2196F3',
                boxSizing: 'border-box',
                fontSize: '13px'
            });

            $content.empty().append($input);
            $input.focus().select();

            const save_value = () => {
                console.log("💾 SAVE_VALUE CALLED");
                
                const input_value = $input.val();
                console.log("Input field contains:", input_value);
                
                const new_value = parseFloat(input_value);

                console.log("Parsed to number:", new_value);

                if (isNaN(new_value) || new_value < 0) {
                    frappe.msgprint(__("Please enter a valid number"));
                    $content.html(`<div style="text-align:right">${current_value.toFixed(2)}</div>`);
                    return;
                }

                console.log("✅ Valid value, saving...");

                // Update report.data
                row_data.approved_overtime_hours = new_value;
                row_data.approved_overtime_amount =
                    new_value * row_data.hourly_rate * row_data.overtime_multiplier;

                console.log("Updated row_data:", {
                    approved_hours: row_data.approved_overtime_hours,
                    approved_amount: row_data.approved_overtime_amount
                });

                // Initialize edited_values if needed
                if (!report.edited_values) {
                    console.log("Initializing edited_values");
                    report.edited_values = {};
                }

                // Save to edited_values
                report.edited_values[row_data.attendance] = {
                    approved_overtime_hours: new_value,
                    calculated_overtime_hours: row_data.overtime_hours
                };

                console.log("✅ Saved to edited_values:", report.edited_values);
                console.log("Edited value for", row_data.attendance, ":", report.edited_values[row_data.attendance]);

                $content.html(`<div style="text-align:right">${new_value.toFixed(2)}</div>`);

                setTimeout(() => update_report_totals(report), 100);

                frappe.show_alert({
                    message: __("Updated to {0} hrs", [new_value.toFixed(2)]),
                    indicator: "blue"
                }, 2);
            };

            $input.on('keypress', e => {
                if (e.which === 13) {
                    console.log("⏎ ENTER pressed");
                    e.preventDefault();
                    save_value();
                }
            });
            
            // Removed blur handler to prevent accidental saves
            // Only Enter will save now
            
            $input.on('keydown', e => {
                if (e.which === 27) {
                    console.log("⎋ ESCAPE pressed");
                    $content.html(`<div style="text-align:right">${current_value.toFixed(2)}</div>`);
                }
            });
        }
    );

    // Visual cue on correct column
    setTimeout(() => {
        $(`.dt-cell--col-${VISUAL_COL_INDEX}:not([data-is-header]):not([data-is-filter])`)
            .css({ cursor: 'text', backgroundColor: '#fffef0' });
        console.log(`✅ Applied yellow background to column ${VISUAL_COL_INDEX}`);
    }, 100);

    console.log("✓ Manual cell editing enabled on column", VISUAL_COL_INDEX);
}

// =====================================================================
// UPDATE TOTALS
// =====================================================================

function update_report_totals(report) {
    if (!report.data) return;
    
    let total_calc = 0;
    let total_appr = 0;
    let total_calc_amount = 0;
    let total_appr_amount = 0;
    
    report.data.forEach(row => {
        total_calc += parseFloat(row.overtime_hours) || 0;
        total_appr += parseFloat(row.approved_overtime_hours) || 0;
        total_calc_amount += parseFloat(row.overtime_amount) || 0;
        total_appr_amount += parseFloat(row.approved_overtime_amount) || 0;
    });
    
    console.log("Totals:", {
        calc_hours: total_calc.toFixed(2),
        appr_hours: total_appr.toFixed(2)
    });
    
    let $total_row = $('.dt-row-totalRow');
    if ($total_row.length > 0) {
        $total_row.find('[data-col-index="9"] .dt-cell__content')
            .html(`<div style="text-align: right">${total_calc.toFixed(2)}</div>`);
        
        $total_row.find('[data-col-index="10"] .dt-cell__content')
            .html(`<div style="text-align: right">${total_appr.toFixed(2)}</div>`);
        
        $total_row.find('[data-col-index="15"] .dt-cell__content')
            .html(`<div style="text-align: right">Sh ${total_calc_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}</div>`);
        
        $total_row.find('[data-col-index="16"] .dt-cell__content')
            .html(`<div style="text-align: right">Sh ${total_appr_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}</div>`);
    }
}

// =====================================================================
// PROCESS SELECTED OVERTIME
// =====================================================================

function process_selected_overtime(report, action) {

    if (!report.datatable) return;

    const checked_indexes = report.datatable.rowmanager
        .getCheckedRows()
        .filter(r => r !== 'totalRow')
        .map(r => parseInt(r, 10));

    if (!checked_indexes.length) {
        frappe.msgprint({
            title: __("No Selection"),
            message: __("Please select at least one record"),
            indicator: "orange"
        });
        return;
    }

    const checked_data = checked_indexes
        .map(i => report.data[i])
        .filter(Boolean);

    console.log("=== PROCESSING ===");
    console.log("Checked rows:", checked_data.length);
    console.log("Edited values:", Object.keys(report.edited_values || {}).length);

    // Merge edits AND recalculate amounts
    checked_data.forEach(row => {
        if (report.edited_values && report.edited_values[row.attendance]) {
            let edited = report.edited_values[row.attendance];
            row.approved_overtime_hours = edited.approved_overtime_hours;
            row.has_custom_hours = true;
            
            // IMPORTANT: Recalculate the approved amount
            row.approved_overtime_amount = row.approved_overtime_hours * row.hourly_rate * row.overtime_multiplier;
            
            console.log(`✓ Custom hours for ${row.attendance}: ${row.approved_overtime_hours} hrs = KES ${row.approved_overtime_amount.toFixed(2)}`);
        } else {
            row.has_custom_hours = false;
            if (!row.approved_overtime_hours) {
                row.approved_overtime_hours = row.overtime_hours;
                row.approved_overtime_amount = row.overtime_amount;
            }
        }
    });
    
    console.log("Data after merging:", checked_data.map(r => ({
        att: r.attendance,
        calc: r.overtime_hours,
        appr: r.approved_overtime_hours,
        appr_amt: r.approved_overtime_amount,
        custom: r.has_custom_hours
    })));
    
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
    let eligible = checked_data.filter(row => row.is_eligible == 1 || row.is_eligible == "1");
    let non_eligible = checked_data.filter(row => row.is_eligible == 0 || row.is_eligible == "0");
    
    if (eligible.length === 0) {
        frappe.msgprint({
            title: __("No Eligible Employees"),
            message: __("None selected are eligible for overtime"),
            indicator: "red"
        });
        return;
    }
    
    let d = new frappe.ui.Dialog({
        title: __("Approve Overtime"),
        fields: [{
            fieldname: "summary_html",
            fieldtype: "HTML",
            options: get_approval_summary(eligible, non_eligible)
        }],
        size: "large",
        primary_action_label: __("Approve & Create Additional Salary"),
        primary_action: function() {
            let attendance_data = eligible.map(row => ({
                attendance: row.attendance,
                approved_overtime_hours: row.approved_overtime_hours,
                has_custom_hours: row.has_custom_hours
            }));
            
            console.log("Sending to backend:", attendance_data);
            
            frappe.call({
                method: "vc_app.vc_overtime.overtime_processor.process_selected_overtime",
                args: {
                    attendance_list: attendance_data,
                    action: "approve"
                },
                freeze: true,
                freeze_message: __("Processing..."),
                callback: function(r) {
                    if (r.message) {
                        let result = r.message;
                        if (result.errors && result.errors.length > 0) {
                            frappe.msgprint({
                                title: __("Completed with Errors"),
                                message: __("Approved: {0}<br>Errors: {1}", 
                                    [result.approved, result.errors.join("<br>")]),
                                indicator: "orange"
                            });
                        } else {
                            frappe.show_alert({
                                message: __("✓ Approved {0} records", [result.approved]),
                                indicator: "green"
                            }, 5);
                        }
                        report.checked_items = [];
                        report.edited_values = {};
                        report.refresh();
                        d.hide();
                    }
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
        title: __("Reject & Reset Times"),
        fields: [{
            fieldname: "warning_html",
            fieldtype: "HTML",
            options: get_rejection_warning(checked_data)
        }],
        size: "large",
        primary_action_label: __("Yes, Reset Times"),
        primary_action: function() {
            let attendance_data = checked_data.map(row => ({
                attendance: row.attendance,
                approved_overtime_hours: row.approved_overtime_hours || 0,
                has_custom_hours: row.has_custom_hours || false
            }));
            
            frappe.call({
                method: "vc_app.vc_overtime.overtime_processor.process_selected_overtime",
                args: {
                    attendance_list: attendance_data,
                    action: "reject"
                },
                freeze: true,
                freeze_message: __("Resetting..."),
                callback: function(r) {
                    if (r.message) {
                        let result = r.message;
                        frappe.show_alert({
                            message: __("✓ Reset {0} times", [result.rejected]),
                            indicator: "blue"
                        }, 5);
                        report.checked_items = [];
                        report.edited_values = {};
                        report.refresh();
                        d.hide();
                    }
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
    let total_calc = 0;
    let total_appr = 0;
    let total_amount = 0;
    let custom_count = 0;
    
    console.log("=== GENERATING APPROVAL SUMMARY ===");
    console.log("Eligible rows:", eligible.length);
    
    eligible.forEach((row, index) => {
        let calc = parseFloat(row.overtime_hours) || 0;
        let appr = parseFloat(row.approved_overtime_hours) || 0;
        let amt = parseFloat(row.approved_overtime_amount) || 0;
        
        console.log(`Row ${index} (${row.attendance}):`, {
            overtime_hours: calc,
            approved_overtime_hours: appr,
            approved_overtime_amount: amt,
            has_custom_hours: row.has_custom_hours
        });
        
        total_calc += calc;
        total_appr += appr;
        total_amount += amt;
        if (row.has_custom_hours) custom_count++;
    });
    
    console.log("Summary Totals:", {
        total_calculated: total_calc.toFixed(2),
        total_approved: total_appr.toFixed(2),
        total_amount: total_amount.toFixed(2),
        custom_count: custom_count
    });
    console.log("=== END SUMMARY ===");
    
    let html = `
        <div style="padding: 20px;">
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #2e7d32;">✓ Approval Summary</h4>
                <table class="table table-bordered" style="margin-top: 15px; background: white;">
                    <tr>
                        <td style="width: 60%; padding: 10px;"><strong>Eligible Employees:</strong></td>
                        <td style="padding: 10px; font-weight: bold;">${eligible.length}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 10px;"><strong>Total Calculated OT:</strong></td>
                        <td style="padding: 10px; color: #607d8b; font-weight: bold;">${total_calc.toFixed(2)} hrs</td>
                    </tr>
                    <tr style="background-color: #e8f5e9;">
                        <td style="padding: 10px;"><strong>Total Approved OT:</strong></td>
                        <td style="padding: 10px; color: #2e7d32; font-weight: bold; font-size: 16px;">${total_appr.toFixed(2)} hrs</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px;"><strong>Total Amount:</strong></td>
                        <td style="padding: 10px; color: green; font-weight: bold; font-size: 20px;">
                            KES ${total_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}
                        </td>
                    </tr>
                </table>
            </div>`;
    
    if (custom_count > 0) {
        html += `
            <div style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin-bottom: 20px;">
                <strong>ℹ️ Custom Hours:</strong> ${custom_count} employee(s) with adjusted hours.
            </div>`;
    }
    
    if (non_eligible.length > 0) {
        html += `
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin-bottom: 20px;">
                <strong>⚠️ Warning:</strong> ${non_eligible.length} not eligible - will be skipped.
            </div>`;
    }
    
    html += `</div>`;
    return html;
}

function get_rejection_warning(checked_data) {
    let custom_count = checked_data.filter(row => row.has_custom_hours).length;
    
    return `
        <div style="padding: 20px;">
            <div style="background-color: #ffebee; padding: 20px; border-radius: 5px; border-left: 4px solid #f44336; margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #c62828;">⚠️ This will reset ${checked_data.length} checkout times</h4>
            </div>
            ${custom_count > 0 ? `
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <strong>ℹ️</strong> ${custom_count} with custom hours will use those for reset.
            </div>` : ''}
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Action:</strong> Reset to In Time + 8h + Approved OT + Allowance ± 5min</p>
            </div>
        </div>`;
}

// =====================================================================
// SUMMARY DIALOG
// =====================================================================

function show_overtime_summary(report) {
    let data = report.data || [];
    let total_hours = 0;
    let total_amount = 0;
    let pending = 0;
    let approved = 0;
    
    data.forEach(row => {
        total_hours += parseFloat(row.overtime_hours) || 0;
        total_amount += parseFloat(row.overtime_amount) || 0;
        if (row.status == "Approved & Paid") approved++;
        else if (row.status == "Pending Review") pending++;
    });
    
    frappe.msgprint({
        title: __("Overtime Summary"),
        message: `
            <b>Total Records:</b> ${data.length}<br>
            <b>Total Hours:</b> ${total_hours.toFixed(2)}<br>
            <b>Total Amount:</b> KES ${total_amount.toLocaleString('en-KE', {minimumFractionDigits: 2})}<br>
            <b>Pending:</b> ${pending}<br>
            <b>Approved:</b> ${approved}
        `,
        indicator: "blue"
    });
}

// =====================================================================
// FILE: Frontend JavaScript for Server-Side Cache
// Replace localStorage with API calls to server cache
// =====================================================================

console.log("=== SERVER-SIDE CACHE SOLUTION ===");

// API wrapper functions
const OvertimeEditAPI = {
    
    // Save an edit to server cache
    saveEdit: async function(attendance, approved_hours) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.save_edit',
                args: {
                    attendance: attendance,
                    approved_hours: approved_hours
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        console.log("💾 Saved to server:", attendance, "→", approved_hours);
                        resolve(r.message);
                    } else {
                        console.error("❌ Save failed:", r.message);
                        reject(r.message);
                    }
                },
                error: function(err) {
                    console.error("❌ API error:", err);
                    reject(err);
                }
            });
        });
    },
    
    // Get all edits for current user
    getEdits: async function() {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.get_edits',
                callback: function(r) {
                    if (r.message && r.message.success) {
                        console.log(`📥 Retrieved ${r.message.count} edits from server`);
                        resolve(r.message.edits || {});
                    } else {
                        console.error("❌ Get edits failed:", r.message);
                        reject(r.message);
                    }
                },
                error: function(err) {
                    console.error("❌ API error:", err);
                    reject(err);
                }
            });
        });
    },
    
    // Get single edit
    getEdit: async function(attendance) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.get_edit',
                args: { attendance: attendance },
                callback: function(r) {
                    if (r.message && r.message.success && r.message.found) {
                        resolve(r.message.edit.approved_hours);
                    } else {
                        resolve(null);
                    }
                },
                error: reject
            });
        });
    },
    
    // Clear all edits
    clearAll: async function() {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.clear_all_edits',
                callback: function(r) {
                    if (r.message && r.message.success) {
                        console.log(`🗑️ Cleared ${r.message.cleared} edits from server`);
                        resolve(r.message);
                    } else {
                        reject(r.message);
                    }
                },
                error: reject
            });
        });
    },
    
    // Mark edits as applied (remove from cache after approval)
    markApplied: async function(attendance_list) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.mark_edits_applied',
                args: { attendance_list: attendance_list },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        console.log(`✅ Marked ${r.message.removed} edits as applied`);
                        resolve(r.message);
                    } else {
                        reject(r.message);
                    }
                },
                error: reject
            });
        });
    },
    
    // Get cache info (debugging)
    getCacheInfo: async function() {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'vc_app.vc_overtime.overtime_edit_cache.get_cache_info',
                callback: function(r) {
                    if (r.message && r.message.success) {
                        console.table(r.message);
                        resolve(r.message);
                    } else {
                        reject(r.message);
                    }
                },
                error: reject
            });
        });
    }
};

// Sync server edits to report.edited_values
async function syncToReport() {
    const edits = await OvertimeEditAPI.getEdits();
    
    frappe.query_report.edited_values = {};
    
    Object.keys(edits).forEach(attendance => {
        const row = frappe.query_report.data.find(r => r.attendance === attendance);
        frappe.query_report.edited_values[attendance] = {
            approved_overtime_hours: edits[attendance].approved_hours,
            calculated_overtime_hours: row ? row.overtime_hours : 0
        };
    });
    
    console.log("✅ Synced to report.edited_values:", frappe.query_report.edited_values);
    return frappe.query_report.edited_values;
}

// Apply stored edits to display
async function applyStoredEdits() {
    if (!frappe.query_report || !frappe.query_report.data) return;
    
    const edits = await OvertimeEditAPI.getEdits();
    let count = 0;
    
    frappe.query_report.data.forEach((row, index) => {
        if (!row.attendance) return;
        
        const edit = edits[row.attendance];
        if (edit) {
            const stored_hours = edit.approved_hours;
            
            row.approved_overtime_hours = stored_hours;
            row.approved_overtime_amount = stored_hours * row.hourly_rate * row.overtime_multiplier;
            
            // Update display
            const $cell = $(`.dt-row-${index} .dt-cell--col-10 .dt-cell__content`);
            $cell.html(`<div style="text-align:right; color: green; font-weight: bold;">${stored_hours.toFixed(2)} ✓</div>`);
            
            count++;
        }
    });
    
    if (count > 0) {
        console.log(`✅ Applied ${count} stored edits from server`);
        await syncToReport();
    }
    
    return count;
}

// Double-click handler with server storage
// =====================================================================
// CORRECTED DOUBLE-CLICK HANDLER - Updates display immediately
// Replace the section starting with "$(frappe.query_report.page.wrapper).on('dblclick.server-cache'..."
// =====================================================================

$(frappe.query_report.page.wrapper).off('dblclick.server-cache');
$(frappe.query_report.page.wrapper).on('dblclick.server-cache',
    '.dt-row:not(.dt-row-header):not(.dt-row-filter):not(.dt-row-totalRow) .dt-cell--col-10 .dt-cell__content',
    async function(e) {
        e.stopPropagation();
        e.preventDefault();
        
        const $clickedCell = $(this);
        const $row = $clickedCell.closest('.dt-row');
        const row_index = $row.data('row-index');
        
        if (row_index === undefined || !frappe.query_report.data[row_index]) return;
        
        const row = frappe.query_report.data[row_index];
        const attendance = row.attendance;
        
        if (row.status === "Approved" || row.status === "Approved & Paid") {
            frappe.show_alert({
                message: "Cannot edit approved records",
                indicator: "red"
            }, 2);
            return;
        }
        
        console.log("🖱️ Editing row", row_index, "attendance:", attendance);
        
        // Get current value from server
        let current_value;
        try {
            current_value = await OvertimeEditAPI.getEdit(attendance);
            if (current_value === null) {
                current_value = row.approved_overtime_hours ?? row.overtime_hours ?? 0;
            }
        } catch (err) {
            current_value = row.approved_overtime_hours ?? row.overtime_hours ?? 0;
        }
        
        // Prompt for new value
        const input = prompt(
            `Edit approved hours for ${row.employee_name}:\n\n` +
            `Original: ${row.overtime_hours} hrs\n` +
            `Current: ${current_value} hrs`,
            current_value
        );
        
        if (input === null) {
            console.log("Canceled");
            return;
        }
        
        const new_value = parseFloat(input);
        
        if (isNaN(new_value) || new_value < 0) {
            frappe.msgprint("Please enter a valid positive number");
            return;
        }
        
        if (new_value > 12) {
            frappe.msgprint({
                title: "Warning",
                message: "You entered more than 12 hours. Please verify.",
                indicator: "orange"
            });
        }
        
        console.log("✅ Saving value:", new_value, "for row:", row_index);
        
        // Show loading
        frappe.show_alert({
            message: "Saving...",
            indicator: "blue"
        }, 1);
        
        try {
            // 1. Save to server cache
            await OvertimeEditAPI.saveEdit(attendance, new_value);
            console.log("✅ Saved to server");
            
            // 2. Update report.data immediately
            row.approved_overtime_hours = new_value;
            row.approved_overtime_amount = new_value * row.hourly_rate * row.overtime_multiplier;
            console.log("✅ Updated report.data");
            
            // 3. Update display - Use fresh selector, not the stale $clickedCell reference
            const cellSelector = `.dt-row-${row_index} .dt-cell--col-10 .dt-cell__content`;
            const $cell = $(cellSelector);
            
            const displayHTML = `<div style="text-align:right; color: green; font-weight: bold;">${new_value.toFixed(2)} ✓</div>`;
            
            // Force update
            $cell.empty();
            $cell.html(displayHTML);
            
            console.log("✅ Updated display");
            console.log("   Selector:", cellSelector);
            console.log("   Found:", $cell.length, "elements");
            console.log("   New HTML:", $cell.html());
            
            // 4. Sync to report.edited_values (but don't re-apply which would overwrite display)
            frappe.query_report.edited_values = frappe.query_report.edited_values || {};
            frappe.query_report.edited_values[attendance] = {
                approved_overtime_hours: new_value,
                calculated_overtime_hours: row.overtime_hours
            };
            console.log("✅ Synced to report.edited_values");
            
            // 5. Visual feedback - flash green background
            $cell.css('background-color', '#d4edda');
            setTimeout(() => {
                $cell.css('background-color', '');
            }, 1000);
            
            frappe.show_alert({
                message: `✓ Saved: ${new_value.toFixed(2)} hrs (Refresh to see changes)`,
                indicator: "green"
            }, 5);

            console.log("✅ Complete! Refresh page to see updated display");
            console.log("✅ Complete! Display updated to:", new_value.toFixed(2));
            
        } catch (error) {
            console.error("❌ Save failed:", error);
            frappe.msgprint({
                title: "Save Failed",
                message: "Could not save edit to server. Please try again.",
                indicator: "red"
            });
        }
    }
);

console.log("✅ Corrected handler attached - display will update immediately!");

// Hook into approval process to mark edits as applied
const original_show_approval_dialog = window.show_approval_dialog;
if (original_show_approval_dialog) {
    window.show_approval_dialog = async function(report, checked_data) {
        // Call original dialog
        original_show_approval_dialog(report, checked_data);
        
        // After approval, mark edits as applied
        const originalPrimaryAction = cur_dialog.get_primary_btn();
        if (originalPrimaryAction) {
            originalPrimaryAction.off('click');
            originalPrimaryAction.on('click', async function() {
                // Let the original approval process
                // Then mark edits as applied
                setTimeout(async () => {
                    const attendance_list = checked_data.map(r => r.attendance);
                    try {
                        await OvertimeEditAPI.markApplied(attendance_list);
                        console.log("✅ Edits marked as applied and removed from cache");
                    } catch (err) {
                        console.error("❌ Could not mark edits as applied:", err);
                    }
                }, 2000);
            });
        }
    };
}

// Apply edits on page load
setTimeout(async () => {
    try {
        await applyStoredEdits();
    } catch (err) {
        console.error("❌ Could not apply stored edits:", err);
    }
}, 1000);

// Expose utilities globally
window.OvertimeEditCache = {
    save: OvertimeEditAPI.saveEdit,
    getAll: OvertimeEditAPI.getEdits,
    getOne: OvertimeEditAPI.getEdit,
    clearAll: OvertimeEditAPI.clearAll,
    info: OvertimeEditAPI.getCacheInfo,
    applyEdits: applyStoredEdits,
    syncToReport: syncToReport
};

console.log("✅ SERVER-SIDE CACHE READY!");
console.log("\n📖 Usage:");
console.log("  - Double-click a cell to edit");
console.log("  - OvertimeEditCache.getAll() - view all edits");
console.log("  - OvertimeEditCache.info() - cache statistics");
console.log("  - OvertimeEditCache.clearAll() - clear all edits");
console.log("\n⏱️ Edits expire after 24 hours");