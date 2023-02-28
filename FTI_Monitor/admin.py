from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Tabless
from .models import Rows

# Register your models here.
admin.site.register(Tabless)
admin.site.register(Rows)