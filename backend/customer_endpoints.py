"""
Enterprise Customer CRM API Endpoints
Created: 22 January 2026
"""

from fastapi import APIRouter, Query
from typing import Optional
from customer_service import CustomerService
import io
import csv
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin/customers", tags=["CRM"])


@router.get("/")
async def get_customers(
    segment: Optional[str] = Query(None, description="Filter by segment: VIP, Active, Regular, At-Risk, Lost"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    sort_by: str = Query("total_spent", description="Sort by: total_spent, total_orders, last_order_date, rfm_score"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Get all customers with RFM scores and segmentation
    """
    result = await CustomerService.get_all_customers(
        segment=segment,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        skip=skip
    )
    
    return result


@router.get("/segments/stats")
async def get_segment_stats():
    """
    Get statistics for all customer segments
    """
    stats = await CustomerService.get_customer_segments_stats()
    return stats


@router.get("/{customer_id}")
async def get_customer_detail(customer_id: str):
    """
    Get detailed customer information with order timeline
    """
    customer = await CustomerService.get_customer_detail(customer_id)
    
    if not customer:
        return {"error": "Customer not found"}, 404
    
    return customer


@router.get("/export/csv")
async def export_customers_csv(
    segment: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Export customers to CSV
    """
    result = await CustomerService.get_all_customers(
        segment=segment,
        search=search,
        limit=10000
    )
    
    customers = result['customers']
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ZOZO Burger - Customer Database Export'])
    writer.writerow([f'Total Customers: {len(customers)}'])
    writer.writerow([])
    
    # Data Header
    writer.writerow([
        'Customer ID', 'Name', 'Email', 'Phone',
        'Total Orders', 'Completed Orders', 'Total Spent (€)',
        'Avg Order Value (€)', 'Days Since Last Order',
        'Customer Lifetime (Days)', 'RFM Score', 'Segment'
    ])
    
    # Data Rows
    for customer in customers:
        writer.writerow([
            customer['customer_id'],
            customer['name'],
            customer['email'] or '',
            customer['phone'] or '',
            customer['total_orders'],
            customer['completed_orders'],
            customer['total_spent'],
            customer['avg_order_value'],
            customer['days_since_last_order'],
            customer['customer_lifetime_days'],
            customer['rfm']['rfm_score'],
            customer['rfm']['segment']
        ])
    
    output.seek(0)
    
    from datetime import datetime
    filename = f"zozo-customers-{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
