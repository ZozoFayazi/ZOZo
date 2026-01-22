"""
Enterprise Finance Management API Endpoints
Created: 22 January 2026
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
from typing import Optional
from finance_service import FinanceService
import io
import csv
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin/finance", tags=["Finance"])


def parse_date_range(range_type: str) -> tuple:
    """Parse date range type to start and end dates"""
    now = datetime.now(timezone.utc)
    
    if range_type == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "yesterday":
        yesterday = now - datetime.timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif range_type == "this_week":
        start = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "last_month":
        # First day of current month
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of previous month
        end = first_of_month - datetime.timedelta(seconds=1)
        # First day of previous month
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif range_type == "this_year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif range_type == "30days":
        start = (now - datetime.timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:  # default to this_month
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    return start, end


@router.get("/overview")
async def get_financial_overview(
    range_type: str = Query("this_month", description="Time range: today, yesterday, this_week, this_month, last_month, this_year, 30days"),
    location_id: Optional[str] = None
):
    """
    Get comprehensive financial overview
    Returns: revenue (gross/net/tax), payment methods, trends
    """
    start_date, end_date = parse_date_range(range_type)
    
    overview = await FinanceService.get_financial_overview(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    return overview


@router.get("/revenue-by-location")
async def get_revenue_by_location(
    range_type: str = Query("this_month")
):
    """
    Get revenue breakdown by location
    """
    start_date, end_date = parse_date_range(range_type)
    
    revenue = await FinanceService.get_revenue_by_location(
        start_date=start_date,
        end_date=end_date,
        branch_ids=None
    )
    
    return {"data": revenue}


@router.get("/revenue-by-category")
async def get_revenue_by_category(
    range_type: str = Query("this_month"),
    location_id: Optional[str] = None
):
    """
    Get revenue breakdown by category
    """
    start_date, end_date = parse_date_range(range_type)
    
    categories = await FinanceService.get_revenue_by_category(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    return {"data": categories}


@router.get("/daily-trend")
async def get_daily_revenue_trend(
    range_type: str = Query("30days"),
    location_id: Optional[str] = None
):
    """
    Get daily revenue trend
    """
    start_date, end_date = parse_date_range(range_type)
    
    trend = await FinanceService.get_daily_revenue_trend(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    return {"data": trend}


@router.get("/top-products")
async def get_top_products(
    range_type: str = Query("this_month"),
    location_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get top products by revenue
    """
    start_date, end_date = parse_date_range(range_type)
    
    products = await FinanceService.get_top_products_by_revenue(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None,
        limit=limit
    )
    
    return {"data": products}


@router.get("/monthly-comparison")
async def get_monthly_comparison(
    year: int = Query(2026, ge=2020, le=2030),
    location_id: Optional[str] = None
):
    """
    Get month-by-month comparison for a year
    """
    comparison = await FinanceService.get_monthly_comparison(
        year=year,
        location_id=location_id,
        branch_ids=None
    )
    
    return {"data": comparison}


@router.get("/export/csv")
async def export_finance_csv(
    range_type: str = Query("this_month"),
    location_id: Optional[str] = None
):
    """
    Export financial data as CSV
    """
    start_date, end_date = parse_date_range(range_type)
    
    # Get all data
    overview = await FinanceService.get_financial_overview(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    daily_trend = await FinanceService.get_daily_revenue_trend(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        branch_ids=None
    )
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ZOZO Burger - Financial Report'])
    writer.writerow([f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'])
    writer.writerow([])
    
    # Overview
    writer.writerow(['Financial Overview'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Revenue (Gross)', f"€{overview['overview']['total_revenue_gross']}"]) 
    writer.writerow(['Total Revenue (Net)', f"€{overview['overview']['total_revenue_net']}"])
    writer.writerow(['Total Tax (19%)', f"€{overview['overview']['total_tax']}"])
    writer.writerow(['Total Orders', overview['overview']['total_orders']])
    writer.writerow(['Avg Order Value', f"€{overview['overview']['avg_order_value']}"])
    writer.writerow(['Revenue Growth', f"{overview['overview']['revenue_growth_percent']}%"])
    writer.writerow([])
    
    # Payment Methods
    writer.writerow(['Payment Methods'])
    writer.writerow(['Method', 'Orders', 'Revenue', 'Percentage'])
    for method, data in overview['payment_methods'].items():
        writer.writerow([method, data['count'], f"€{data['revenue']}", f"{data['percentage']}%"])
    writer.writerow([])
    
    # Daily Trend
    writer.writerow(['Daily Revenue Trend'])
    writer.writerow(['Date', 'Revenue (Gross)', 'Revenue (Net)', 'Tax', 'Orders'])
    for day in daily_trend:
        writer.writerow([
            day['date'],
            f"€{day['revenue_gross']}",
            f"€{day['revenue_net']}",
            f"€{day['tax']}",
            day['orders']
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=zozo-finance-{start_date.strftime('%Y%m%d')}.csv"
        }
    )
