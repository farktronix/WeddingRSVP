from reply.models import Reply, Person, FailedAttempt, ReplyLog, InviteEmail
from django.contrib import admin

admin.site.register(Reply)
admin.site.register(Person)
admin.site.register(FailedAttempt)
admin.site.register(ReplyLog)
admin.site.register(InviteEmail)