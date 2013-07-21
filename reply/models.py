from django.db import models

class Person(models.Model):
    firstName = models.CharField(max_length=256, verbose_name="First Name")
    lastName = models.CharField(max_length=256, verbose_name="Last Name")
    nickName = models.CharField(max_length=256, blank=True, verbose_name="Nickname")
    
    def __unicode__(self):
        nameStr = self.firstName.capitalize()
        if (self.lastName is not None):
          nameStr = nameStr + " " + self.lastName.capitalize()
        return nameStr

class Reply(models.Model):
    invitedPeople = models.ManyToManyField(Person, related_name='Invite', verbose_name="Invited People")
    attendingPeople = models.ManyToManyField(Person, related_name='+', blank=True, verbose_name="Attending People")
    
    maxAttendees = models.IntegerField(default=1, verbose_name="Max Attendees")
    
    email = models.EmailField(blank=True, verbose_name="Email Address")
    
    comment = models.TextField(blank=True, verbose_name="Comment")
    
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    replyDate = models.DateTimeField(blank=True, verbose_name="Reply Date")
    lastModDate = models.DateTimeField(auto_now=True, verbose_name="Last Mod Date")
    
    def __unicode__(self):
        description = "Invite (" + str(self.maxAttendees) + " people) (" + ', '.join(str(x) for x in self.invitedPeople.all()) + ') '
        if (self.replyDate):
            if (len(self.attendingPeople.all())):
                description = description + 'Attending: (' + ', '.join(str(x) for x in self.attendingPeople.all()) + ') '
            else:
                description = description + "NOT attending "
            description = description + " Reply date: " + str(self.replyDate) + " from " + self.ip
        else:
            description = description + "No reply"
        return description