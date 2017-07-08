from django.contrib import admin

from .models import Profile, Service

admin.site.register(Profile)
admin.site.register(Service)
# Register your models here.
'''
from django.contrib import admin

# Register your models here
from .models import Program,ProgramData,ProgramScenario, Company, CompanyData

admin.site.register(Company)
admin.site.register(CompanyData)

admin.site.register(Program)
admin.site.register(ProgramData)
admin.site.register(ProgramScenario)
'''
