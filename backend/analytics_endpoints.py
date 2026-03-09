"""
Analytics API Endpoints for ZOZO Burger
Created: 22 January 2026
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, timezone
from typing import Optional
from analytics_service import AnalyticsService
import io
import csv
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin/analytics", tags=["Analytics"])

# Import auth dependency (will be added to server.py)
# from server import get_current_admin


def parse_date_range(range_type: str) -> tuple:
    """
    Parse date range type to start and end dates
    Options: today, yesterday, 7days, 30days, custom
    """
    now = datetime.now(timezone.utc)
    
    if range_type == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif range_type == "7days":
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "30days":
        start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:  # default to today
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    return start, end


@router.get("/overview")
async def get_analytics_overview(
    range_type: str = Query("today", description="Time range: today, yesterday, 7days, 30days"),
    location_id: Optional[str] = Query(None, description="Filter by location"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    # admin: dict = Depends(get_current_admin)  # Uncomment when integrated
):
    """
    Get comprehensive analytics overview
    Returns: revenue, orders, customers, avg order value with trends
    """
    # Parse date range
    if start_date and end_date:
        # Custom date range
        pass
    else:
        start_date, end_date = parse_date_range(range_type)
    
    # TODO: Get branch_ids from admin permissions
    # branch_ids = admin.get('branch_ids', [])
    branch_ids = None  # For now, allow all
    
    stats = await AnalyticsService.get_overview_stats(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=branch_ids
    )
    
    return {
        "period": {
            "range_type": range_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "stats": stats
    }


@router.get("/revenue-trend")
async def get_revenue_trend(
    range_type: str = Query("7days"),
    location_id: Optional[str] = None,
    granularity: str = Query("day", description="Granularity: day, week, month"),
    # admin: dict = Depends(get_current_admin)
):
    """
    Get revenue trend over time
    Returns: array of {date, revenue, orders}
    """
    start_date, end_date = parse_date_range(range_type)
    
    trend = await AnalyticsService.get_revenue_trend(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None,
        granularity=granularity
    )
    
    return {
        "period": {
            "range_type": range_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "granularity": granularity,
        "data": trend
    }


@router.get("/top-products")
async def get_top_products(
    range_type: str = Query("30days"),
    location_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    # admin: dict = Depends(get_current_admin)
):
    """
    Get top-selling products
    Returns: array of {name, quantity, revenue}
    """
    start_date, end_date = parse_date_range(range_type)
    
    products = await AnalyticsService.get_top_products(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None,
        limit=limit
    )
    
    return {
        "period": {
            "range_type": range_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": products
    }


@router.get("/peak-hours")
async def get_peak_hours(
    range_type: str = Query("7days"),
    location_id: Optional[str] = None,
    # admin: dict = Depends(get_current_admin)
):
    """
    Get peak hours analysis
    Returns: {hour: order_count} for 24 hours
    """
    start_date, end_date = parse_date_range(range_type)
    
    peak_hours = await AnalyticsService.get_peak_hours(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    # Convert to array format for easier charting
    data = [
        {"hour": hour, "orders": count}
        for hour, count in sorted(peak_hours.items())
    ]
    
    return {
        "period": {
            "range_type": range_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": data
    }


@router.get("/location-comparison")
async def get_location_comparison(
    range_type: str = Query("30days"),
    # admin: dict = Depends(get_current_admin)
):
    """
    Compare performance across locations
    Returns: array of {location, revenue, orders, avg_order_value}
    """
    start_date, end_date = parse_date_range(range_type)
    
    comparison = await AnalyticsService.get_location_comparison(
        start_date=start_date,
        end_date=end_date,
        branch_ids=None
    )
    
    return {
        "period": {
            "range_type": range_type,
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data": comparison
    }


@router.get("/export/csv")
async def export_analytics_csv(
    range_type: str = Query("30days"),
    location_id: Optional[str] = None,
    # admin: dict = Depends(get_current_admin)
):
    """
    Export analytics data as CSV
    """
    start_date, end_date = parse_date_range(range_type)
    
    # Get all data
    overview = await AnalyticsService.get_overview_stats(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    top_products = await AnalyticsService.get_top_products(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None,
        limit=20
    )
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ZOZO Burger Analytics Report'])
    writer.writerow([f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'])
    writer.writerow([])
    
    # Overview Stats
    writer.writerow(['Overview Statistics'])
    writer.writerow(['Metric', 'Value', 'Change %'])
    writer.writerow(['Total Revenue', f"€{overview['revenue']['total']}", f"{overview['revenue']['change']}%"])
    writer.writerow(['Total Orders', overview['orders']['total'], f"{overview['orders']['change']}%"])
    writer.writerow(['Avg Order Value', f"€{overview['avg_order_value']['value']}", f"{overview['avg_order_value']['change']}%"])
    writer.writerow([])
    
    # Top Products
    writer.writerow(['Top Products'])
    writer.writerow(['Rank', 'Product', 'Quantity Sold', 'Revenue'])
    for idx, product in enumerate(top_products, 1):
        writer.writerow([idx, product['name'], product['quantity'], f"€{product['revenue']}"])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=zozo-analytics-{start_date.strftime('%Y%m%d')}.csv"
        }
    )
