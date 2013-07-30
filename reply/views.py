from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from reply.models import Person, Reply, FailedAttempt, ReplyLog, InviteEmail
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
    elif len(queryResults) > 1:
        try:
            # Filter out any people that aren't on a reply
            queryResults = [x for x in queryResults if len(x.reply_invite.all())]
            
            allLookSame=True
            invite_id = queryResults[0].reply_invite.all()[0].pk
            firstName = queryResults[0].firstName
            lastName = queryResults[0].lastName
            for person in queryResults:
                if person.firstName == firstName and person.lastName == lastName:
                    continue
                if person.reply_invite.all()[0].pk != invite_id:
                    allLookSame=False
                    break
            if allLookSame:
                p = queryResults[0]
        except:
            pass
    return (p, len(queryResults))
    
def _personFromNameComponents(firstName, lastName):
    maxResults = 0
    # Check for a strict first and last name match
    if firstName is not None and lastName is not None:
        (p, results) = _personForQuery(Person.objects.filter(firstName__iexact=firstName, lastName__iexact=lastName))
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
    
    # Check for a strict first name match.
    if firstName is not None:
        (p, results)  = _personForQuery(Person.objects.filter(firstName__iexact=firstName))
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
    
        # Check for a nickanme match
        (p, results)  = _personForQuery(Person.objects.filter(nickName__iexact=firstName))
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
            
        # Maybe they typed in just their last name.
        (p, results)  = _personForQuery(Person.objects.filter(lastName__iexact=firstName))
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
    
    # Check for a strict last name match.
    if lastName is not None:
        (p, results)  = _personForQuery(Person.objects.filter(lastName__iexact=lastName))
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
    
    return (None, maxResults)

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
    
    maxResults = 0
    (p, results) = _personFromNameComponents(firstName, lastName)
    if p is not None:
        return (p, 0)
    else:
        maxResults = max(maxResults, results)
    
    if len(nameComps) > 2:
        # Maybe they have a two word first name (Mary Beth)
        firstName = nameComps[0] + " " + nameComps[1]
        lastName = nameComps[2]
        
        (p, results) = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
        
        # Maybe it's a two word last name (Du Bois)
        firstName = nameComps[0] 
        lastName = nameComps[1] + " " + nameComps[2]
        
        (p, results) = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
        
    elif len(nameComps) == 2:
        # Maybe they have a two word first name (Mary Beth)
        firstName = nameComps[0] + " " + nameComps[1]
        lastName = None
        
        (p, results) = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
        
        # Maybe it's a two word last name (Du Bois)
        firstName = None
        lastName = nameComps[1] + " " + nameComps[2]
        
        (p, results) = _personFromNameComponents(firstName, lastName)
        if p is not None:
            return (p, 0)
        else:
            maxResults = max(maxResults, results)
    
    return (None, maxResults)
    

def index(request):
    name = request.POST.get('name')
    if name is None or len(name) == 0:
       return newreply(request)
    else:
        p = None
        numResults = 0
        r = None
        
        try:
            (p, numResults) = _personFromName(name)
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
                    
            r.views = r.views + 1
            r.save()
            
            return render_to_response('reply.html', {
                "person" : p,
                "reply"  : r,
                "plusOnePerson" : plusOnePerson,
                "greeting" : ["Hello", "Hi", "Howdy", "Welcome"],
                "inviteEmails" : ", ".join(sorted((e.email for e in r.emails.all()))),
            }, context_instance=RequestContext(request))
        else:
            try:
                f = FailedAttempt(query=name, ip=_get_client_ip(request))
                f.save()
            except:
                pass
            if (numResults == 0):
                return newreply(request, "Sorry, " + name.capitalize() + "- we couldn't find your name in the RSVP list. Please try again with your full name.")
            else:
                return newreply(request, "Sorry, " + name.capitalize() + "- too many people match that name. Can you try again with something more specific?")
        
def updatereply(request):
    reply = None
    try:
        reply = Reply.objects.get(pk=request.POST.get('reply_id'))
    except:
        pass
        
    if reply == None:    
        return newreply(request, "We couldn't find your name in the RSVP list. Please try again with your full name.")
        
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
            plusOneAttending = request.POST.getlist('attendeePlusOne')
            if plusOneAttending is not None and len(plusOneAttending) > 0:
                reply.plusOneAttending = True

                # Create the plus one person if necessary
                plusOneName = request.POST.get('plusOneName')
                if plusOneName is not None:
                    plusOnePerson = None
                    try:
                        (plusOnePerson, numResults) = _personFromName(plusOneName)
                    except:
                        pass
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
            else:
                reply.plusOneAttending = False
    elif willAttend == "no":
        reply.attending = False
        reply.plusOneAttending = False
    
    emails = request.POST.get('emails')
    reply.emails.clear()
    for email in emails.split(','):
        e = InviteEmail()
        e.email = email.strip()
        e.save()
        reply.emails.add(e)
    
    reply.comment = request.POST.get('comment')
    
    reply.replyDate = datetime.datetime.now()
    reply.ip = _get_client_ip(request)
        
    reply.save()
    
    log = ReplyLog()
    log.ip = _get_client_ip(request)
    log.reply = reply
    log.save()
    log.initWithReply(reply)
    log.save()
    
    return render_to_response('replyupdated.html', {
        "reply"  : reply,
        "replyName" : reply._attendeeName()
    }, context_instance=RequestContext(request))

def newreply(request, error_message=None):
    context = {}
    if error_message is not None:
        context['error_message'] = error_message
    return render_to_response('newreply.html', context, context_instance=RequestContext(request))
    