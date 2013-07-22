from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from reply.models import Person, Reply, FailedAttempt

def index(request):
    return render_to_response('summary.html', {
        'replyYes' : Reply.objects.filter(attending=True),
        'replyNo'  : Reply.objects.filter(attending=False, replyDate__isnull=False),
        'replyNone' : Reply.objects.filter(replyDate__isnull=True),
    }, context_instance=RequestContext(request))
    
def newreply(request):
    return render_to_response('adminNewReply.html', {
        'numPeople' : xrange(6)
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
        r.email = request.POST.get('email')
        r.hasPlusOne = request.POST.get('allowPlusOne') or False
        r.save()
    
    return render_to_response('adminNewReply.html', {
        'numPeople' : xrange(6),
        'lastReply' : r,
    }, context_instance=RequestContext(request))