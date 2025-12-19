# =====================================================================
# FILE: vc_app/vc_overtime/overtime_edit_cache.py
# Server-side session cache for overtime edits
# =====================================================================

import frappe
import json
from frappe import _
import logging

logging.basicConfig(level=logging.DEBUG)
@frappe.whitelist()
def save_edit(attendance, approved_hours):
    """
    Save an overtime edit to server cache
    
    Args:
        attendance: Attendance record ID (e.g., HR-ATT-2025-00376)
        approved_hours: Edited hours (float)
    
    Returns:
        dict: Success message with saved data
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        # Get existing edits
        edits = frappe.cache().hget(cache_key, "data")
        if edits:
            edits = json.loads(edits)
        else:
            edits = {}
        
        # Add/update this edit
        edits[attendance] = {
            "approved_hours": float(approved_hours),
            "timestamp": frappe.utils.now(),
            "edited_by": user
        }
        
        # Save back to cache (expires in 24 hours)
        frappe.cache().hset(cache_key, "data", json.dumps(edits))
        frappe.cache().expire(cache_key, 86400)  # 24 hours
        
        frappe.logger().info(f"Saved edit: {attendance} → {approved_hours} hrs (user: {user})")
        
        return {
            "success": True,
            "attendance": attendance,
            "approved_hours": float(approved_hours),
            "total_edits": len(edits)
        }
        
    except Exception as e:
        frappe.log_error(f"Error saving overtime edit: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_edits():
    """
    Get all pending edits for current user
    
    Returns:
        dict: All edits keyed by attendance ID
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        edits = frappe.cache().hget(cache_key, "data")
        
        if edits:
            edits = json.loads(edits)
            frappe.logger().info(f"Retrieved {len(edits)} edits for user: {user}")
            return {
                "success": True,
                "edits": edits,
                "count": len(edits)
            }
        else:
            return {
                "success": True,
                "edits": {},
                "count": 0
            }
            
    except Exception as e:
        frappe.log_error(f"Error retrieving overtime edits: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "edits": {}
        }


@frappe.whitelist()
def get_edit(attendance):
    """
    Get a single edit by attendance ID
    
    Args:
        attendance: Attendance record ID
    
    Returns:
        dict: Edit data or None
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        edits = frappe.cache().hget(cache_key, "data")
        
        if edits:
            edits = json.loads(edits)
            edit = edits.get(attendance)
            
            if edit:
                return {
                    "success": True,
                    "found": True,
                    "edit": edit
                }
        
        return {
            "success": True,
            "found": False,
            "edit": None
        }
        
    except Exception as e:
        frappe.log_error(f"Error retrieving overtime edit: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def delete_edit(attendance):
    """
    Delete a single edit
    
    Args:
        attendance: Attendance record ID
    
    Returns:
        dict: Success message
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        edits = frappe.cache().hget(cache_key, "data")
        
        if edits:
            edits = json.loads(edits)
            if attendance in edits:
                del edits[attendance]
                frappe.cache().hset(cache_key, "data", json.dumps(edits))
                
                return {
                    "success": True,
                    "deleted": True,
                    "remaining": len(edits)
                }
        
        return {
            "success": True,
            "deleted": False,
            "message": "Edit not found"
        }
        
    except Exception as e:
        frappe.log_error(f"Error deleting overtime edit: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def clear_all_edits():
    """
    Clear all edits for current user
    
    Returns:
        dict: Success message
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        # Get count before clearing
        edits = frappe.cache().hget(cache_key, "data")
        count = 0
        if edits:
            count = len(json.loads(edits))
        
        # Clear cache
        frappe.cache().delete_key(cache_key)
        
        frappe.logger().info(f"Cleared {count} edits for user: {user}")
        
        return {
            "success": True,
            "cleared": count
        }
        
    except Exception as e:
        frappe.log_error(f"Error clearing overtime edits: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def mark_edits_applied(attendance_list):
    """
    Mark edits as applied after approval (removes them from cache)
    
    Args:
        attendance_list: List of attendance IDs that were approved
    
    Returns:
        dict: Success message
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        edits = frappe.cache().hget(cache_key, "data")
        
        if edits:
            edits = json.loads(edits)
            
            # Parse attendance_list if it's a string
            if isinstance(attendance_list, str):
                attendance_list = json.loads(attendance_list)
            
            # Remove applied edits
            removed = 0
            for attendance in attendance_list:
                if attendance in edits:
                    del edits[attendance]
                    removed += 1
            
            # Save updated cache
            if edits:
                frappe.cache().hset(cache_key, "data", json.dumps(edits))
            else:
                frappe.cache().delete_key(cache_key)
            
            frappe.logger().info(f"Marked {removed} edits as applied for user: {user}")
            
            return {
                "success": True,
                "removed": removed,
                "remaining": len(edits)
            }
        
        return {
            "success": True,
            "removed": 0,
            "remaining": 0
        }
        
    except Exception as e:
        frappe.log_error(f"Error marking edits as applied: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_cache_info():
    """
    Get information about cached edits (for debugging)
    
    Returns:
        dict: Cache statistics
    """
    try:
        user = frappe.session.user
        cache_key = f"overtime_edits_{user}"
        
        edits = frappe.cache().hget(cache_key, "data")
        
        if edits:
            edits = json.loads(edits)
            
            # Get TTL (time to live)
            ttl = frappe.cache().ttl(cache_key)
            
            return {
                "success": True,
                "user": user,
                "cache_key": cache_key,
                "edit_count": len(edits),
                "ttl_seconds": ttl,
                "ttl_hours": round(ttl / 3600, 2),
                "edits": edits
            }
        else:
            return {
                "success": True,
                "user": user,
                "cache_key": cache_key,
                "edit_count": 0,
                "ttl_seconds": 0,
                "message": "No edits in cache"
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting cache info: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }