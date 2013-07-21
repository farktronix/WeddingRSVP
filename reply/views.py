from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from reply.models import Person, Reply, FailedAttempt
import datetime

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def _personForQuery(queryResults):
    p = None
    if len(queryResults) == 1:
        p = queryResults[0]
    else:
        try:
            allLookSame=True
            invite_id = queryResults[0].Invite.all()[0].pk
            for person in queryResults:
                if person.Invite.all()[0].pk != invite_id:
                    allLookSame=False
                    break
            if allLookSame:
                p = queryResults[0]
        except:
            pass
    return p
    
def _personFromNameComponents(firstName, lastName):
    # Check for a strict first and last name match
    if firstName is not None and lastName is not None:
        p = _personForQuery(Person.objects.filter(firstName__iexact=firstName, lastName__iexact=lastName))
        if p is not None:
            return p
    
    # Check for a strict first name match.
    if firstName is not None:
        p = _personForQuery(Person.objects.filter(firstName__iexact=firstName))
        if p is not None:
            return p
    
        # Check for a nickanme match
        p = _personForQuery(Person.objects.filter(nickName__iexact=firstName))
        if p is not None:
            return p
            
        # Maybe they typed in just their last name.
        p = _personForQuery(Person.objects.filter(lastName__iexact=firstName))
        if p is not None:
            return p
    
    # Check for a strict last name match.
    if lastName is not None:
        p = _personForQuery(Person.objects.filter(lastName__iexact=lastName))
        if p is not None:
            return p
    
    return None

def _personFromName(name):
    if name is None or len(name) == 0:
        return None
    if name.lower() == 'guest':
        return None
        
    nameComps = name.split()
    firstName = None
    lastName = None
    
    if len(nameComps) > 0:
        firstName = nameComps[0]
    if len(nameComps) > 1:
        lastName = nameComps[1]
    
    p = _personFromNameComponents(firstName, lastName)
    if p is not None:
        return p
    
    if len(nameComps) > 2:
        # Maybe they have a two word first name (Mary Beth)
        firstName = nameComps[0] + " " + nameComps[1]
        lastName = nameComps[2]
        
        p = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return p
        
        # Maybe it's a two word last name (Du Bois)
        firstName = nameComps[0] 
        lastName = nameComps[1] + " " + nameComps[2]
        
        p = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return p
        
    elif len(nameComps) == 2:
        # Maybe they have a two word first name (Mary Beth)
        firstName = nameComps[0] + " " + nameComps[1]
        lastName = None
        
        p = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return p
        
        # Maybe it's a two word last name (Du Bois)
        firstName = None
        lastName = nameComps[1] + " " + nameComps[2]
        
        p = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return p
    
    return None
    

def index(request):
    name = request.POST.get('name')
    if name is None or len(name) == 0:
       return newreply(request, "Please enter a name")
    else:
        p = None
        r = None
        
        try:
            p = _personFromName(name)
        except:
            pass
        
        try:
            r = p.reply_invite.all()[0]
            if len(r.invitedPeople.all()) == 1 and not r.hasPlusOne and not r.plusOneAttending:
                r.hasPlusOne = True
                r.plusOneAttending = False
        except:
            pass
            
        if p and r:
            plusOnePerson = None
            for person in r.attendingPeople.all():
                if person.isPlusOne:
                    plusOnePerson = person
                    break
            
            return render_to_response('reply.html', {
                "person" : p,
                "reply"  : r,
                "plusOnePerson" : plusOnePerson
            }, context_instance=RequestContext(request))
        else:
            try:
                f = FailedAttempt(query=name, ip=_get_client_ip(request))
                f.save()
            except:
                pass
            return newreply(request, "We couldn't find your name in the RSVP list. Please try again.")
        
def updatereply(request, reply_uuid):
    reply = None
    try:
        reply = Reply.objects.filter(uuid=reply_uuid)[0]
    except:
        pass
        
    if reply == None:    
        return newreply(request, "We couldn't find your name in the RSVP list. Please try again.")
        
    reply.attendingPeople.clear()
    
    willAttend = request.POST.get('willAttend')
    if willAttend == "yes":
        reply.attending = True
        
        for personID in request.POST.getlist('attendee'):
            try:
                p = Person.objects.get(pk=personID)
                if p is not None:
                    reply.attendingPeople.add(p)
            except:
                pass
                
        if reply.hasPlusOne:
            if request.POST.getlist('plusOneAttending') is not None:
                reply.plusOneAttending = True
            else:
                reply.plusOneAttending = False

        # Create the plus one person if necessary
        plusOneName = request.POST.get('plusOneName')
        if plusOneName is not None:
            plusOnePerson = _personFromName(plusOneName)
            if plusOnePerson is None and plusOneName.lower() != 'guest':
                # Create a new +1 person
                nameComps = plusOneName.split()
                firstName = ""
                lastName = ""

                if len(nameComps) > 0:
                    firstName = nameComps[0].capitalize()
                if len(nameComps) > 1:
                    lastName = nameComps[1].capitalize()

                plusOnePerson = Person(firstName=firstName, lastName=lastName, isPlusOne=True)
                plusOnePerson.save()
            if plusOnePerson is not None:
                reply.attendingPeople.add(plusOnePerson)
    elif willAttend == "no":
        reply.attending = False
        reply.plusOneAttending = False
    
    reply.comment = request.POST.get('comment')
    
    reply.replyDate = datetime.datetime.now()
    reply.ip = _get_client_ip(request)
        
    reply.save()
    
    return render_to_response('replyupdated.html', {
        "reply"  : reply,
    }, context_instance=RequestContext(request))

def newreply(request, error_message=None):
    return render_to_response('newreply.html', {'error_message' : error_message}, context_instance=RequestContext(request))
    