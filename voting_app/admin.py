from django.contrib import admin
from . import models

admin.site.site_header ="Voting System"
admin.site.site_title = "voting Admin Area"
admin.site.index_title = "Welcome to the Voting Admin"

class Voters(admin.ModelAdmin):
    list_display = ('user_fname', 'user_lname', 'user_email',)
    readonly_fields = ('has_voted',)

class Candidates(admin.ModelAdmin):
    list_display = ('name', 'position')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'position')


admin.site.register(models.Position)
admin.site.register(models.Voter, Voters)
admin.site.register(models.Candidate, Candidates)
admin.site.register(models.Vote, VoteAdmin)
