from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from reply.models import Person, Reply, FailedAttempt, InviteEmail

def index(request):
    attending = Reply.objects.filter(attending=True).all()
    notAttending = Reply.objects.filter(attending=False, replyDate__isnull=False).all()
    noReply = Reply.objects.filter(replyDate__isnull=True).all()
    
    numAttending = 0
    numNotAttending = 0
    numNotReplied = 0
    for reply in attending:
        reply.summaryText = reply._attendeeName()
        reply.allInvited = reply.allNames()
        reply.numAttending = len(reply.attendingPeople.all())
        numAttending = numAttending + len(reply.attendingPeople.all())
    
    for reply in notAttending:
        reply.summaryText = reply._attendeeName()
        reply.allInvited = reply.allNames()
        numNotAttending = numNotAttending + len(reply.invitedPeople.all())
        
    for reply in noReply:
        reply.summaryText = reply._attendeeName()
        reply.allInvited = reply.allNames()
        numNotReplied = numNotReplied + len(reply.invitedPeople.all())
        
        
    return render_to_response('summary.html', {
        'replyYes' : sorted(attending, key=lambda reply: reply.replyDate, reverse=True),
        'replyNo'  : sorted(notAttending, key=lambda reply: reply.replyDate, reverse=True),
        'replyNone' : sorted(noReply, key=lambda reply: reply.replyDate, reverse=True),
        'numAttending' : numAttending,
        'numNotAttending' : numNotAttending,
        'numNotReplied' : numNotReplied,
    }, context_instance=RequestContext(request))

def emails(request):
    replies = Reply.objects.filter().all()
    for reply in replies:
        reply.summaryText = reply._attendeeName()
        reply.emailString = ", ".join((r.email for r in reply.emails.all()))
    
    return render_to_response('emails.html', {
        'replies' : sorted(replies, key=lambda reply: len(reply.emails.all())),
    }, context_instance=RequestContext(request))
    
def updateemails(request):
    replyID = request.POST.get('replyid')
    reply = None
    try:
        reply = Reply.objects.get(pk=replyID)
    except:
        pass
    
    if reply is None:
        return render_to_response('emailUpdate.html', {
            'errorText' : "Error updating person: not found",
        }, context_instance=RequestContext(request))
        
    
    emails = request.POST.get('emails')
    for email in reply.emails.all():
        email.delete()
    for email in emails.split(','):
        e = InviteEmail()
        e.email = email.strip()
        e.save()
        reply.emails.add(e)
        
    reply.save()
    return render_to_response('emailUpdate.html', {
        'resultText' : "Email address updated for " + reply._attendeeName(),
    }, context_instance=RequestContext(request))
    
def newreply(request):
    return render_to_response('adminNewReply.html', {
        'numPeople' : xrange(6)
    }, context_instance=RequestContext(request))
    
def listpeople(request):
    return render_to_response('listpeople.html', {
        'allPeople' : Person.objects.all()
    }, context_instance=RequestContext(request))
    
def updateperson(request):
    personID = request.POST.get('personid')
    person = None
    try:
        person = Person.objects.get(pk=personID)
    except:
        pass
    
    if person is None:
        return render_to_response('emailUpdate.html', {
            'errorText' : "Error updating person: not found",
        }, context_instance=RequestContext(request))
    
    person.imageURL = request.POST.get('imageURL')
    person.nickName = request.POST.get('nickName')
    person.save()
    
    return render_to_response('emailUpdate.html', {
        'resultText' : "Person updated:  " + unicode(person),
    }, context_instance=RequestContext(request))
    
def createupdate(request):
    allPeople = []
    for i in xrange(6):
        firstName = request.POST.get('firstName' + str(i))
        if firstName is not None and len(firstName) > 0:
            lastName = request.POST.get('lastName' + str(i)) or ""
            nickName = request.POST.get('nickName' + str(i)) or ""
            preferNick = request.POST.get('preferNick' + str(i)) or False
            allPeople.append(Person(firstName=firstName, 
                       lastName=lastName, 
                       nickName=nickName,
                       prefersNickName=preferNick))
    
    r = None
    if len(allPeople) > 0:
        r = Reply()
        r.ip="127.0.0.1"
        r.save()
        for p in allPeople:
            p.save()
            r.invitedPeople.add(p)
            r.attendingPeople.add(p)
        emails = request.POST.get('email')
        for email in emails.split(','):
            e = InviteEmail()
            e.email = email.strip()
            e.save()
            r.emails.add(e)
        r.hasPlusOne = request.POST.get('allowPlusOne') or False
        r.save()
    
    return render_to_response('adminNewReply.html', {
        'numPeople' : xrange(6),
        'lastReply' : r,
    }, context_instance=RequestContext(request))
