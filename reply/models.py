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
    
    mustAttend = models.BooleanField(default=False, verbose_name="Must Attend")
    
    def __unicode__(self):
        if self.prefersNickName:
            return unicode(self.nickName)
        
        nameStr = unicode(self.firstName)
        if self.lastName is not None:
            nameStr = nameStr + " " + unicode(self.lastName)
        return nameStr
        
class InviteEmail(models.Model):
    email = models.EmailField(blank=True, verbose_name="Email Address")

    def __unicode__(self):
        return self.email

class Reply(models.Model):
    uuid = UUIDField(unique=True, editable=False)
    
    invitedPeople = models.ManyToManyField(Person, related_name='%(class)s_invite', verbose_name="Invited People")
    attendingPeople = models.ManyToManyField(Person, related_name='+', blank=True, verbose_name="Attending People")

    attending = models.BooleanField(default=False, verbose_name="Attending")
      
    hasPlusOne = models.BooleanField(default=False, verbose_name="Plus One") 
    plusOneAttending = models.BooleanField(default=False, verbose_name="Plus One Attending")
    
    emails = models.ManyToManyField(InviteEmail, blank=True, verbose_name="Email Addresses")
        
    comment = models.TextField(blank=True, verbose_name="Comment")
    
    views = models.IntegerField(default=0, verbose_name="View Count")
    
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    replyDate = models.DateTimeField(blank=True, null=True, verbose_name="Reply Date")
    lastModDate = models.DateTimeField(auto_now=True, verbose_name="Last Mod Date")
    
    # Deprecated
    email = models.EmailField(blank=True, verbose_name="Email Address")
    
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

    def allNames(self):
        retval = "Invited: "
        for person in self.invitedPeople.all():
            personName = person.firstName
            if person.lastName is not None and len(person.lastName):
                personName = personName + " " + person.lastName
            if person.nickName is not None and len(person.nickName):
                personName = personName + " (" + person.nickName
                if person.prefersNickName:
                    personName = personName + " * "
                personName = personName +  ")"
            retval = retval + personName + ", "
        return retval
    
    def __unicode__(self):
        return self._inviteName()
        
class ReplyLog(models.Model):
    reply = models.ForeignKey(Reply, related_name='+')
    
    attendees = models.ManyToManyField(Person, related_name='%(class)s_replylog', blank=True, verbose_name="Attending People")

    attending = models.BooleanField(default=False, verbose_name="Attending")
      
    hasPlusOne = models.BooleanField(default=False, verbose_name="Plus One") 
    plusOneAttending = models.BooleanField(default=False, verbose_name="Plus One Attending")
    
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    lastModDate = models.DateTimeField(auto_now=True, verbose_name="Last Mod Date")
    
    def initWithReply(self, r):
        self.reply = r
        for person in r.attendingPeople.all():
             self.attendees.add(person)
        self.attending = r.attending
        self.hasPlusOne = r.hasPlusOne
        self.plusOneAttending = r.plusOneAttending
        
    def __unicode__(self):
        return self.reply._inviteName() + ": " + unicode(self.ip) + "@ " + unicode(self.lastModDate) + " (" + unicode(self.attending) + ")"

class FailedAttempt(models.Model):
    query = models.TextField(verbose_name="Name")
    ip = models.IPAddressField(blank=True, verbose_name="IP Address")
    date = models.DateTimeField(auto_now=True, verbose_name="Date")
    
    def __unicode__(self):
        return "\"" + self.query + "\" (" + self.ip + " @ " + str(self.date) + ")"
