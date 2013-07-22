from reply.models import Person, Reply, FailedAttempt

def index(request):
    return render_to_response('summary.html', {}, context_instance=RequestContext(request))
    
def newreply(request):
    return render_to_response('adminNewReply.html', {
        "person" : p,
        "reply"  : r,
        "plusOnePerson" : plusOnePerson,
        "greeting" : ["Hello", "Hi", "Howdy", "Welcome"],
    }, context_instance=RequestContext(request))
    
def updatereply(request):
    return index(request)