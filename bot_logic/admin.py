from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(TelegramBot)
admin.site.register(Restaurant)
admin.site.register(RestaurantBranch)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(StudentInfo)
admin.site.register(StudentSettings)
admin.site.register(TheoryTopic)
admin.site.register(TheoryBlock)
admin.site.register(TheoryTest)
admin.site.register(StudentTest)
admin.site.register(TestQuestion)
admin.site.register(TestAnswer)
admin.site.register(StudentAnswer)
admin.site.register(TelegramMessage)