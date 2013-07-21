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

    attending = models.BooleanField(default=False, verbose_name="Attending")
      
    hasPlusOne = models.BooleanField(default=False, verbose_name="Plus One") 
    plusOneAttending = models.BooleanField(default=False, verbose_name="Plus One Attending")
    
    email = models.EmailField(blank=True, verbose_name="Email Address")
    
    comment = models.TextField(blank=True, verbose_name="Comment")
    
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    replyDate = models.DateTimeField(blank=True, null=True, verbose_name="Reply Date")
    lastModDate = models.DateTimeField(auto_now=True, verbose_name="Last Mod Date")
    
    def __unicode__(self):
        description = "Invite (" + ', '.join(str(x) for x in self.invitedPeople.all()) + ') '
        if (self.hasPlusOne):
            description = description + " + 1 "
        if (self.replyDate):
            if (len(self.attendingPeople.all())):
                description = description + 'Attending: (' + ', '.join(str(x) for x in self.attendingPeople.all()) + ') '
            else:
                description = description + "NOT attending "
            description = description + " Reply date: " + str(self.replyDate) + " from " + self.ip
        else:
            description = description + "No reply"
        return description

class FailedAttempt(models.Model):
    query = models.TextField(verbose_name="Name")
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    date = models.DateTimeField(auto_now=True, verbose_name="Date")
    
    def __unicode__(self):
        return "\"" + self.query + "\" (" + self.ip + " @ " + str(self.date) + ")"