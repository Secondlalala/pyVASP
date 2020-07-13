from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from order.models import OrderDB
import pandas as pd

# Create your views here.
def index(request) :
    c = list(OrderDB.objects.filter(person='cee'))
    b = list(OrderDB.objects.order_by('OrderID'))
    pd_b = pd.DataFrame(b)
    context = {
        'var1' : "member",
        'num_order' : len(OrderDB.objects.all()),
        'cee' : pd_b
    }
    return render(request, 'index.html', context)

'''
def index(request) :
    template = loader.get_template('index.html')
    context = {
        'var1' : "member"
    }
    return HttpResponse(template.render(context,request))

def index(request) :
    return HttpResponse("<h1>CTM order manager</h1>")
'''

def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)