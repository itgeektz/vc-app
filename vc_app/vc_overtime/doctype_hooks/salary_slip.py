# =====================================================================
# FILE: vc_app/vc_overtime/doctype_hooks/salary_slip.py
# Server-side hook to aggregate duplicate salary components in Salary Slip
# =====================================================================

import frappe
from frappe import _
from frappe.utils import flt

def before_save(doc, method=None):
    """
    Aggregate duplicate salary components in earnings and deductions.
    This runs before the Salary Slip is saved.
    
    Problem: Multiple Additional Salary entries with same component create duplicates
    Solution: Aggregate amounts and combine references
    
    Example:
        Before: OT-WD: 3281.99, OT-WD: 3281.99
        After:  OT-WD: 6563.98
    """
    if doc.docstatus > 0:
        # Don't modify submitted documents
        return
    
    # Aggregate earnings
    if doc.earnings:
        original_count = len(doc.earnings)
        doc.earnings = aggregate_salary_details(doc.earnings, "Earnings")
        new_count = len(doc.earnings)
        
        if new_count < original_count:
            frappe.msgprint(
                _("Aggregated {0} duplicate earning components into {1} entries").format(
                    original_count, new_count
                ),
                alert=True,
                indicator="blue"
            )
    
    # Aggregate deductions
    if doc.deductions:
        original_count = len(doc.deductions)
        doc.deductions = aggregate_salary_details(doc.deductions, "Deductions")
        new_count = len(doc.deductions)
        
        if new_count < original_count:
            frappe.msgprint(
                _("Aggregated {0} duplicate deduction components into {1} entries").format(
                    original_count, new_count
                ),
                alert=True,
                indicator="blue"
            )


def aggregate_salary_details(details, detail_type=""):
    """
    Aggregate duplicate salary components while preserving all data.
    
    Args:
        details: List of Salary Detail child table rows
        detail_type: "Earnings" or "Deductions" (for logging)
    
    Returns:
        List of aggregated Salary Detail rows
    """
    if not details or len(details) <= 1:
        return details
    
    # Group by salary component
    component_map = {}
    
    for detail in details:
        component = detail.salary_component
        
        if component not in component_map:
            # First occurrence - initialize
            component_map[component] = {
                'detail': detail,
                'additional_salaries': [],
                'amount': flt(detail.amount, 2),
                'additional_amount': flt(detail.additional_amount, 2),
                'default_amount': flt(detail.default_amount, 2),
                'year_to_date': flt(detail.year_to_date, 2),
                'count': 1,
                'first_idx': detail.idx
            }
            
            # Track additional salary reference
            if hasattr(detail, 'additional_salary') and detail.additional_salary:
                component_map[component]['additional_salaries'].append(detail.additional_salary)
        else:
            # Duplicate found - aggregate amounts
            component_map[component]['amount'] += flt(detail.amount, 2)
            component_map[component]['additional_amount'] += flt(detail.additional_amount, 2)
            component_map[component]['default_amount'] += flt(detail.default_amount, 2)
            component_map[component]['year_to_date'] += flt(detail.year_to_date, 2)
            component_map[component]['count'] += 1
            
            # Track additional additional salary reference
            if hasattr(detail, 'additional_salary') and detail.additional_salary:
                component_map[component]['additional_salaries'].append(detail.additional_salary)
    
    # Build aggregated list
    aggregated = []
    idx = 1
    
    for component, data in component_map.items():
        detail = data['detail']
        
        if data['count'] > 1:
            # Multiple entries found - update with aggregated values
            detail.amount = flt(data['amount'], 2)
            detail.additional_amount = flt(data['additional_amount'], 2)
            detail.default_amount = flt(data['default_amount'], 2)
            detail.year_to_date = flt(data['year_to_date'], 2)
            
            # Combine additional salary references
            if data['additional_salaries']:
                if hasattr(detail, 'additional_salary'):
                    detail.additional_salary = ", ".join(data['additional_salaries'])
            
            # Add aggregation note (optional - comment out if not needed)
            # if hasattr(detail, 'description'):
            #     original_desc = detail.description or ""
            #     detail.description = f"{original_desc} [Aggregated from {data['count']} entries]".strip()
        
        # Update index to maintain order
        detail.idx = idx
        idx += 1
        
        aggregated.append(detail)
    
    return aggregated


def validate(doc, method=None):
    """
    Optional: Additional validation after aggregation
    """
    pass


def on_submit(doc, method=None):
    """
    Optional: Log aggregation details for audit trail
    """
    # Count overtime components
    overtime_components = []
    
    for earning in doc.earnings:
        if "overtime" in earning.salary_component.lower():
            if hasattr(earning, 'additional_salary') and earning.additional_salary:
                # Check if aggregated (contains comma)
                if "," in earning.additional_salary:
                    count = len(earning.additional_salary.split(","))
                    overtime_components.append(f"{earning.salary_component} (aggregated from {count} entries)")
                else:
                    overtime_components.append(earning.salary_component)
    
    if overtime_components:
        frappe.logger().info(
            f"Salary Slip {doc.name} includes overtime: {', '.join(overtime_components)}"
        )