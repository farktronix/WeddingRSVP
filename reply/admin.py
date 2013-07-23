from reply.models import Reply, Person, FailedAttempt, ReplyLog
from django.contrib import admin

admin.site.register(Reply)
admin.site.register(Person)
admin.site.register(FailedAttempt)
admin.site.register(ReplyLog)