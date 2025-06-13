from django.contrib import admin
from store_app.models import member,commodity,faceID

# Register your models here.
# admin.site.register(member)

class Admin_member_show_field(admin.ModelAdmin):
    list_display = ('id', 'cName', 'cSex', 'cEmail', 'cPassward', 'cPhoto1' , 'cPhoto2' , 'cPhoto3')
    search_fields = ('cName',)
    ordering = ('id',)

admin.site.register(member,Admin_member_show_field)

class Admin_commodity_show_field(admin.ModelAdmin):
    list_display = ('id','commodity_Name','commodity_price','commodity_image')
    search_fields = ('commodity_Name',)
    ordering = ('id',)

admin.site.register(commodity,Admin_commodity_show_field)

class Admin_faceID_show_field(admin.ModelAdmin):
    list_display = ('id','faceID_name','faceID_number')
    search_fields = ('faceID_name',)
    ordering = ('id',)
admin.site.register(faceID,Admin_faceID_show_field)