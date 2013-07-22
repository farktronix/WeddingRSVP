from django.db import models
import uuid

class UUIDField(models.CharField) :
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 64 )
        kwargs['blank'] = True
        models.CharField.__init__(self, *args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add :
            value = str(uuid.uuid4())
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(models.CharField, self).pre_save(model_instance, add)

class Person(models.Model):
    firstName = models.CharField(max_length=256, verbose_name="First Name")
    lastName = models.CharField(max_length=256, blank=True, verbose_name="Last Name")
    
    nickName = models.CharField(max_length=256, blank=True, verbose_name="Nickname")
    prefersNickName = models.BooleanField(default=False, verbose_name="Prefers Nickname")
    
    isPlusOne = models.BooleanField(default=False, verbose_name="Is Plus One")
    
    imageURL = models.CharField(max_length=512, blank=True, verbose_name="Picture")
    
    def __unicode__(self):
        if self.prefersNickName:
            return unicode(self.nickName)
        
        nameStr = unicode(self.firstName)
        if self.lastName is not None:
            nameStr = nameStr + " " + unicode(self.lastName)
        return nameStr

class Reply(models.Model):
    uuid = UUIDField(unique=True, editable=False)
    
    invitedPeople = models.ManyToManyField(Person, related_name='%(class)s_invite', verbose_name="Invited People")
    attendingPeople = models.ManyToManyField(Person, related_name='+', blank=True, verbose_name="Attending People")

    attending = models.BooleanField(default=False, verbose_name="Attending")
      
    hasPlusOne = models.BooleanField(default=False, verbose_name="Plus One") 
    plusOneAttending = models.BooleanField(default=False, verbose_name="Plus One Attending")
    
    email = models.EmailField(blank=True, verbose_name="Email Address")
    
    comment = models.TextField(blank=True, verbose_name="Comment")
    
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    replyDate = models.DateTimeField(blank=True, null=True, verbose_name="Reply Date")
    lastModDate = models.DateTimeField(auto_now=True, verbose_name="Last Mod Date")
    
    def _inviteName(self):
        invitedPeopleCount = len(self.invitedPeople.all())
        if invitedPeopleCount == 0:
            return "Somebody"
        elif invitedPeopleCount == 1:
            nameString = unicode(self.invitedPeople.all()[0])
            if self.hasPlusOne:
                nameString = nameString + " +1"
            return nameString
        else:
            lastName = unicode(self.invitedPeople.all()[0].lastName)
            allLookSame = True
            for person in self.invitedPeople.all():
                if person.lastName != lastName:
                    allLookSame = False
                    break
            if allLookSame:
                if invitedPeopleCount == 2:
                    return unicode(self.invitedPeople.all()[0].firstName) + " and " + unicode(self.invitedPeople.all()[1].firstName) + " "+ unicode(self.invitedPeople.all()[0].lastName)
                else:
                    return "The " + lastName + " Family (" + unicode(invitedPeopleCount) + ")"
            else:
                joinStr = ", "
                if invitedPeopleCount == 2:
                    joinStr = " and "
                return joinStr.join(unicode(x) for x in self.invitedPeople.all())
        return "[ERROR]"
        
    def _attendeeName(self):
        invitedPeopleCount = len(self.attendingPeople.all())
        if invitedPeopleCount == 0:
            return self._inviteName()
        elif invitedPeopleCount == 1:
            return unicode(self.attendingPeople.all()[0])
        else:
            lastName = unicode(self.attendingPeople.all()[0].lastName)
            allLookSame = True
            for person in self.attendingPeople.all():
                if person.lastName != lastName:
                    allLookSame = False
                    break
            if allLookSame:
                if invitedPeopleCount == 2:
                    return unicode(self.attendingPeople.all()[0].firstName) + " and " + unicode(self.attendingPeople.all()[1].firstName) + " "+ unicode(self.attendingPeople.all()[0].lastName)
                else:
                    return "The " + lastName + " Family (" + unicode(invitedPeopleCount) + ")"
            else:
                joinStr = ", "
                if invitedPeopleCount == 2:
                    joinStr = " and "
                return joinStr.join(unicode(x) for x in self.attendingPeople.all())
        return "[ERROR]"
    
    def __unicode__(self):
        return self._inviteName()

class FailedAttempt(models.Model):
    query = models.TextField(verbose_name="Name")
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    date = models.DateTimeField(auto_now=True, verbose_name="Date")
    
    def __unicode__(self):
        return "\"" + self.query + "\" (" + self.ip + " @ " + str(self.date) + ")"