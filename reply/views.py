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

def _personFromName(name):
    nameComps = name.split()
    firstName = None
    lastName = None
    
    if len(nameComps) > 0:
        firstName = nameComps[0]
    if len(nameComps) > 1:
        lastName = nameComps[1]
        
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
    
    return p
    

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
            r = p.Invite.all()[0]
        except:
            pass
            
        if p and r:    
            return render_to_response('reply.html', {
                "person" : p,
                "reply"  : r,
            }, context_instance=RequestContext(request))
        else:
            try:
                f = FailedAttempt(query=name, ip=_get_client_ip(request))
                f.save()
            except:
                pass
            return newreply(request, "We couldn't find your name in the RSVP list. Please try again.")
        
def updatereply(request, reply_id):
    reply = None
    try:
        reply = Reply.objects.get(pk=reply_id)
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
    elif willAttend == "no":
        reply.attending = False
    
    plusOneAttending = None
    if reply.hasPlusOne:
        if request.POST.get('plusOneAttending') is not None:
            reply.plusOneAttending = True
        else:
            reply.plusOneAttending = False
    
    reply.comment = request.POST.get('comment')
    
    reply.replyDate = datetime.datetime.now()
    reply.ip = _get_client_ip(request)
        
    reply.save()
    
    return render_to_response('replyupdated.html', {
        "reply"  : reply,
    }, context_instance=RequestContext(request))
            
def detail(request, reply_id):
    reply = Reply.objects.get(pk=reply_id)
    return HttpResponse("Hello, " + str(reply))

def newreply(request, error_message=None):
    return render_to_response('newreply.html', {'error_message' : error_message}, context_instance=RequestContext(request))
    