from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Tabless
from .models import Rows
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required(login_url='/')
def index(request):

    return render(request,'home/index.html')

def addTable(request):
    if request.method=="POST":
        instance=Tabless(
            name=request.POST.get('tablename')
        )
        instance.save()
    return redirect(dashpage)

def addRows(request):
    if request.method=="POST":
        instance=Rows(
            Tables=Tabless.objects.get(name=request.POST.get('tablee')),
            Teilindikator=request.POST.get('Teilindikator'),
            Datenquelle=request.POST.get('Datenquelle'),
            Datum=request.POST.get('Datum'),
            Status=request.POST.get('Status'),
            Wert=request.POST.get('Wert'),
            Top3=request.POST.get('Top3'),
            EUDurchschnitt=request.POST.get('Durchschnitt')
        )
        instance.save()
    return redirect(dashpage)

def dashpage(request):
    tables=Tabless.objects.all()
    result=Rows.objects.all()

    return render(request,'home/Krieslaufwirtschaft.html',{"tables":tables, "result":result,"i":0})

def editTable(request):
    if request.method=="POST":
        tab=Tabless.objects.get(name=request.POST.get('tableoldname'))
        tab.name=request.POST.get('tablenewname')
        print(tab.name)
        tab.save()
    return redirect(dashpage)

def editrows(request):
    print(request.POST.get('Datum'))
    if request.method=="POST":
        instance=Rows.objects.get(id=request.POST.get('recordid'))
        instance.Teilindikator=request.POST.get('Teilindikator')
        instance.Datenquelle=request.POST.get('Datenquelle')
        instance.Datum=request.POST.get('Datum')
        instance.Status=request.POST.get('Status')
        instance.Wert=request.POST.get('Wert')
        instance.Top3=request.POST.get('Top3')
        instance.EUDurchschnitt=request.POST.get('Durchschnitt')
        instance.save()
    return redirect(dashpage)

def deleterows(request):
    if request.method=="POST":
        instance=Rows.objects.get(id=request.POST.get('recordid'))
        instance.delete()
    return redirect(dashpage)