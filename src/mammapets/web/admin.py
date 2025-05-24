from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import Pet, Client, MammaPet, Contract, PetCareLog

admin.site.register(Pet)
admin.site.register(Client)
admin.site.register(MammaPet)
admin.site.register(Contract)
admin.site.register(PetCareLog)