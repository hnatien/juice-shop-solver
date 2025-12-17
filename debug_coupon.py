from z85_utils import generate_coupon
import datetime

print("Coupon for today:", generate_coupon(99))
# Try previous month
last_month = datetime.datetime.now() - datetime.timedelta(days=30)
print("Coupon for last month:", generate_coupon(99, date=last_month))
# Try next month
next_month = datetime.datetime.now() + datetime.timedelta(days=30)
print("Coupon for next month:", generate_coupon(99, date=next_month))
