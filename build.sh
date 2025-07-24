# این فایل و دستورات کاملا مربوط به بارگذاری سایت روی سرورهای سایت رندر است

set -o errexit
pip install -r requirements.txt
python manage.py migrate
# خط زیر مربوط به ساخت یوزر ادمین برای سایت هنگام بارگذاری روی سرور است
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput