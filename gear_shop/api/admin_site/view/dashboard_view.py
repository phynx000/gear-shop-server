# api/views/dashboard_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, time, timedelta

from ...permissions import IsAdminUser, IsStaffUser

from api.models import Order, CustomUser
from api.models.stock import Stock


class DashboardOverviewView(APIView):
    permission_classes = [IsStaffUser]  # Only staff/admin can access

    def get(self, request):
        try:
            # Get date ranges
            today = timezone.localdate()
            today_start = timezone.make_aware(datetime.combine(today, time.min))
            today_end = timezone.make_aware(datetime.combine(today, time.max))

            # Weekly range (last 7 days)
            week_start = today_start - timedelta(days=6)

            # Monthly range (current month)
            month_start = today.replace(day=1)
            month_start = timezone.make_aware(datetime.combine(month_start, time.min))

            # Calculate all metrics
            total_orders = Order.objects.count()

            today_orders = Order.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end
            ).count()

            # Today revenue - only completed payments
            today_revenue_paid = Order.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end,
                is_paid=True,
                payment_status='Paid'
            ).aggregate(revenue=Sum('total_price'))['revenue'] or 0

            # Today revenue - pending payments (COD)
            today_revenue_pending = Order.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end,
                payment_status='PendingCOD'
            ).aggregate(revenue=Sum('total_price'))['revenue'] or 0

            # Total all-time revenue (paid orders)
            total_revenue_paid = Order.objects.filter(
                is_paid=True,
                payment_status='Paid'
            ).aggregate(revenue=Sum('total_price'))['revenue'] or 0

            # Weekly revenue (last 7 days)
            weekly_revenue = Order.objects.filter(
                created_at__gte=week_start,
                created_at__lte=today_end,
                is_paid=True,
                payment_status='Paid'
            ).aggregate(revenue=Sum('total_price'))['revenue'] or 0

            # Monthly revenue (current month)
            monthly_revenue = Order.objects.filter(
                created_at__gte=month_start,
                created_at__lte=today_end,
                is_paid=True,
                payment_status='Paid'
            ).aggregate(revenue=Sum('total_price'))['revenue'] or 0

            # Revenue by payment status
            payment_status_revenue = {}
            for status_code, status_name in Order.PAYMENT_STATUS_CHOICES:
                revenue = Order.objects.filter(
                    payment_status=status_code
                ).aggregate(revenue=Sum('total_price'))['revenue'] or 0
                payment_status_revenue[status_code] = int(revenue)

            total_users = CustomUser.objects.count()

            low_stock_items = Stock.objects.filter(quantity__lt=10).count()

            # Return the dashboard data
            return Response({
                "total_orders": total_orders,
                "today_orders": today_orders,
                "today_revenue": {
                    "paid": int(today_revenue_paid),
                    "pending_cod": int(today_revenue_pending),
                    "total": int(today_revenue_paid + today_revenue_pending)
                },
                "total_revenue": int(total_revenue_paid),
                "weekly_revenue": int(weekly_revenue),
                "monthly_revenue": int(monthly_revenue),
                "revenue_by_payment_status": payment_status_revenue,
                "total_users": total_users,
                "low_stock_items": low_stock_items
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve dashboard data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderStatsView(APIView):
    permission_classes = [IsStaffUser]  # Only staff/admin can access

    def get(self, request):
        try:
            # Get the last 7 days
            end_date = timezone.localdate()
            start_date = end_date - timedelta(days=6)  # 7 days including today

            # Initialize data containers
            labels = []
            order_counts = []
            revenue = []

            # Loop through each day and get stats
            current_date = start_date
            while current_date <= end_date:
                # Format date for label
                labels.append(current_date.strftime('%Y-%m-%d'))

                # Create date range for this day
                day_start = timezone.make_aware(datetime.combine(current_date, time.min))
                day_end = timezone.make_aware(datetime.combine(current_date, time.max))

                # Count orders for this day
                day_order_count = Order.objects.filter(
                    created_at__gte=day_start,
                    created_at__lte=day_end
                ).count()
                order_counts.append(day_order_count)

                # Calculate revenue for this day (only paid orders)
                day_revenue = Order.objects.filter(
                    created_at__gte=day_start,
                    created_at__lte=day_end,
                    is_paid=True
                ).aggregate(daily_revenue=Sum('total_price'))['daily_revenue'] or 0
                revenue.append(int(day_revenue))

                # Move to next day
                current_date += timedelta(days=1)

            return Response({
                "labels": labels,
                "order_counts": order_counts,
                "revenue": revenue
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve order statistics: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LowStockProductsView(APIView):
    permission_classes = [IsStaffUser]  # Only staff/admin can access

    def get(self, request):
        try:
            low_stock_threshold = 10

            # Query for products with low stock
            low_stock_items = Stock.objects.filter(
                quantity__lt=low_stock_threshold
            ).select_related('product', 'branch').order_by('quantity')

            # Format the response
            result = []
            for item in low_stock_items:
                result.append({
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "branch_name": item.branch.name,
                    "color": item.color,
                    "quantity": item.quantity
                })

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve low stock products: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )