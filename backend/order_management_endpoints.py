"""
Enterprise Order Management Endpoints
Features: Store Transfer, Manual Override, Error Logs
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId
import logging

from admin_auth import get_current_admin
from utils import serialize_doc
from audit_service import AuditService

class StoreTransferRequest(BaseModel):
    new_location_id: str
    reason: Optional[str] = None
    push_to_pos: bool = True

class ManualOverrideRequest(BaseModel):
    reason: str
    override_type: str = "manual_processing"  # manual_processing, phone_order, etc.

def create_order_management_router(db, audit_service: AuditService, pos_service):
    router = APIRouter(prefix="/api/admin/orders", tags=["Order Management"])
    
    @router.post("/{order_id}/transfer-store")
    async def transfer_order_to_store(
        order_id: str,
        transfer: StoreTransferRequest,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Transfer order to different store/branch
        Use case: Customer called wrong store, order needs to be moved
        """
        try:
            # Get original order - try both ObjectId and string ID
            try:
                order = await db.orders.find_one({"_id": ObjectId(order_id)})
            except:
                order = await db.orders.find_one({"_id": order_id})
            
            if not order:
                # Try by id field
                order = await db.orders.find_one({"id": order_id})
            
            if not order:
                raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
            
            # Get new location
            new_location = await db.locations.find_one({"id": transfer.new_location_id})
            if not new_location:
                try:
                    new_location = await db.locations.find_one({"_id": ObjectId(transfer.new_location_id)})
                except:
                    pass
            
            if not new_location:
                raise HTTPException(status_code=404, detail="Ziel-Filiale nicht gefunden")
            
            old_location_id = order.get('location_id')
            old_location_slug = order.get('location_slug', '')
            new_location_slug = new_location.get('slug', '')
            
            # Check admin permissions for target location
            if admin["role"] != "super_admin":
                branch_ids = admin.get("branch_ids", [])
                if transfer.new_location_id not in branch_ids and new_location_slug not in branch_ids:
                    raise HTTPException(
                        status_code=403, 
                        detail="Keine Berechtigung für Ziel-Filiale"
                    )
            
            # Update order
            update_data = {
                "location_id": transfer.new_location_id,
                "location_slug": new_location_slug,
                "transferred_at": datetime.now(timezone.utc),
                "transferred_by": admin["email"],
                "transfer_reason": transfer.reason,
                "original_location_id": old_location_id,
                "original_location_slug": old_location_slug,
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Add to status history
            status_entry = {
                "status": "transferred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": f"Übertragen von {old_location_slug} nach {new_location_slug}. Grund: {transfer.reason or 'Nicht angegeben'}",
                "admin": admin["email"]
            }
            
            await db.orders.update_one(
                {"_id": order.get('_id')},
                {
                    "$set": update_data,
                    "$push": {"status_history": status_entry}
                }
            )
            
            # Push to new store's POS if requested
            pos_result = {"success": False, "message": "Nicht an POS gesendet"}
            if transfer.push_to_pos:
                try:
                    updated_order = await db.orders.find_one({"_id": order.get('_id')})
                    
                    pos_order_data = {
                        "order_id": str(order.get('_id')),
                        "order_number": updated_order.get('order_number'),
                        "customer_name": updated_order['customer'].get('name'),
                        "customer_email": updated_order['customer'].get('email'),
                        "customer_phone": updated_order['customer'].get('phone'),
                        "items": updated_order['items'],
                        "total": updated_order['total'],
                        "delivery_type": "pickup" if updated_order.get('is_pickup') else "delivery",
                        "delivery_address": f"{updated_order['customer'].get('address', '')}, {updated_order['customer'].get('postal_code', '')} {updated_order['customer'].get('city', '')}",
                        "payment_method": updated_order.get('payment_method', 'cash'),
                        "notes": f"ÜBERTRAGEN VON {old_location_slug}. {updated_order['customer'].get('notes', '')}"
                    }
                    
                    pos_result = await pos_service.push_order(pos_order_data, new_location_slug)
                    
                    # Update POS status
                    await db.orders.update_one(
                        {"_id": order.get('_id')},
                        {
                            "$set": {
                                "pos_status": pos_result.get('pos_status', 'pending'),
                                "pos_pushed_at": datetime.now(timezone.utc),
                                "pos_order_id": pos_result.get('pos_order_id')
                            }
                        }
                    )
                    
                except Exception as e:
                    logging.error(f"POS push after transfer failed: {str(e)}")
                    pos_result = {"success": False, "message": str(e)}
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="order_store_transfer",
                result="success",
                target=order_id,
                target_type="order",
                details={
                    "from_location": old_location_slug,
                    "to_location": new_location_slug,
                    "reason": transfer.reason,
                    "pos_pushed": transfer.push_to_pos,
                    "pos_result": pos_result
                }
            )
            
            return {
                "success": True,
                "message": f"Bestellung erfolgreich nach {new_location.get('name')} übertragen",
                "new_location": {
                    "id": transfer.new_location_id,
                    "name": new_location.get('name'),
                    "slug": new_location_slug
                },
                "pos_result": pos_result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Store transfer error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Fehler beim Übertragen: {str(e)}")
    
    
    @router.post("/{order_id}/manual-override")
    async def mark_order_manual(
        order_id: str,
        override: ManualOverrideRequest,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Mark order as manually processed
        Use case: Order handled by phone/in-person, doesn't need POS integration
        """
        try:
            # Get order - flexible ID handling
            try:
                order = await db.orders.find_one({"_id": ObjectId(order_id)})
            except:
                order = await db.orders.find_one({"_id": order_id})
            
            if not order:
                order = await db.orders.find_one({"id": order_id})
            
            if not order:
                raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
            
            # Check access
            if admin["role"] != "super_admin":
                location_slug = order.get('location_slug', '')
                if location_slug not in admin.get("branch_ids", []):
                    raise HTTPException(status_code=403, detail="Zugriff verweigert")
            
            # Update order
            status_entry = {
                "status": "manual_override",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "note": f"Manuell bearbeitet: {override.reason}",
                "admin": admin["email"],
                "override_type": override.override_type
            }
            
            await db.orders.update_one(
                {"_id": order.get('_id')},
                {
                    "$set": {
                        "manual_override": True,
                        "manual_override_by": admin["email"],
                        "manual_override_at": datetime.now(timezone.utc),
                        "manual_override_reason": override.reason,
                        "manual_override_type": override.override_type,
                        "pos_status": "manual",
                        "updated_at": datetime.now(timezone.utc)
                    },
                    "$push": {"status_history": status_entry}
                }
            )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="order_manual_override",
                result="success",
                target=order_id,
                target_type="order",
                details={
                    "reason": override.reason,
                    "override_type": override.override_type
                }
            )
            
            return {
                "success": True,
                "message": "Bestellung als manuell bearbeitet markiert"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Manual override error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Markieren")
    
    
    @router.get("/{order_id}/error-log")
    async def get_order_error_log(
        order_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Get detailed error log for an order
        Shows POS push attempts, failures, timestamps
        """
        try:
            # Get order - flexible ID handling
            try:
                order = await db.orders.find_one({"_id": ObjectId(order_id)})
            except:
                order = await db.orders.find_one({"_id": order_id})
            
            if not order:
                order = await db.orders.find_one({"id": order_id})
            
            if not order:
                raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
            
            # Check access
            if admin["role"] != "super_admin":
                location_slug = order.get('location_slug', '')
                if location_slug not in admin.get("branch_ids", []):
                    raise HTTPException(status_code=403, detail="Zugriff verweigert")
            
            # Collect error information
            error_log = {
                "order_id": order_id,
                "order_number": order.get('order_number'),
                "current_status": order.get('status'),
                "pos_status": order.get('pos_status', 'unknown'),
                "errors": [],
                "attempts": []
            }
            
            # POS error from order
            if order.get('pos_error'):
                error_log["errors"].append({
                    "type": "pos_push",
                    "message": order.get('pos_error'),
                    "timestamp": order.get('pos_pushed_at', order.get('created_at'))
                })
            
            # Check failed POS orders collection
            failed_orders = await db.failed_pos_orders.find({
                "order_data.order_id": order_id
            }).to_list(length=10)
            
            for failed in failed_orders:
                error_log["attempts"].append({
                    "timestamp": failed.get('created_at'),
                    "error_message": failed.get('error_message'),
                    "error_details": failed.get('error_details'),
                    "status": failed.get('status', 'failed'),
                    "resolved_at": failed.get('resolved_at'),
                    "resolved_by": failed.get('resolved_by')
                })
            
            # Status history for context
            error_log["status_history"] = order.get('status_history', [])
            
            # Additional context
            error_log["order_info"] = {
                "created_at": order.get('created_at'),
                "location": order.get('location_slug'),
                "payment_method": order.get('payment_method'),
                "total": order.get('total'),
                "is_pickup": order.get('is_pickup', False)
            }
            
            return serialize_doc(error_log)
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error log retrieval error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Laden des Fehlerprotokolls")
    
    
    @router.get("/{order_id}/details")
    async def get_order_details(
        order_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Get complete order details with all metadata
        """
        try:
            # Get order - flexible ID handling
            try:
                order = await db.orders.find_one({"_id": ObjectId(order_id)})
            except:
                order = await db.orders.find_one({"_id": order_id})
            
            if not order:
                order = await db.orders.find_one({"id": order_id})
            
            if not order:
                raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
            
            # Check access
            if admin["role"] != "super_admin":
                location_slug = order.get('location_slug', '')
                if location_slug not in admin.get("branch_ids", []):
                    raise HTTPException(status_code=403, detail="Zugriff verweigert")
            
            # Get location details
            location = await db.locations.find_one({"slug": order.get('location_slug')})
            if not location:
                location = await db.locations.find_one({"id": order.get('location_id')})
            
            order_details = serialize_doc(order)
            order_details["location_details"] = serialize_doc(location) if location else None
            
            # Add computed fields
            order_details["is_pos_failed"] = order.get('pos_status') in ['error', 'failed']
            order_details["is_transferred"] = bool(order.get('transferred_at'))
            order_details["is_manual_override"] = order.get('manual_override', False)
            
            return order_details
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Order details error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Laden der Details")
    
    return router
