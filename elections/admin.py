from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from django.contrib.auth.models import User

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (
        ProfileInline,
    )

# Register your models here.

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# admin.site.register(Post)
# admin.site.register(ImagePost)
admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(UserType)
admin.site.register(AllowToVote)
admin.site.register(BallotCast)
admin.site.register(CompleteBallot)
admin.site.register(AllowToRegister)
admin.site.register(Result)