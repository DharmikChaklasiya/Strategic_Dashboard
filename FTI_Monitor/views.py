import asyncio
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Tabless
from .models import Rows
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import eurostat
import pandas as pd
import requests
import xml.etree.ElementTree as ET


@login_required(login_url='/')
def index(request):

    return render(request,'home/index.html')

def addTable(request):
    if request.method=="POST":
        strTable=request.POST.get('tablename').replace(" ","_")
        instance=Tabless(
            name=strTable
        )
        instance.save()
    return redirect(dashpage)

def addRows(request):
    if request.method=="POST":
        strreplace=request.POST.get('tablee').replace(" ","_")
        strreplaceTelli=request.POST.get('Teilindikator').replace(" ","_")
        datasetcode=request.POST.get('datasetcode')
        try:
            data = eurostat.get_data_df(datasetcode)
            if data.empty:
                print('Data not available')
                redirect(dashpage)
            else:
                filteredAT=data.loc[data['geo\\TIME_PERIOD'] == "AT"]
                filteredATLastcolumn=filteredAT.iloc[0,len(filteredAT.columns)-1]
                print(filteredATLastcolumn)
                if filteredATLastcolumn.isnull():
                     filteredATLastcolumn="NaN"
                lastcol=data.columns[len(data.columns)-1]
                lastcolumndf=data.sort_values(by=[lastcol],ascending=False)
                top3=lastcolumndf.head(3)
                topavg=top3[[lastcol]].mean()
                # Define a list of European country codes
                european_countries = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]

                # Filter the DataFrame to only include European countries
                df = data.loc[data['geo\TIME_PERIOD'].isin(european_countries)]
                lastcolname=df.columns[len(data.columns)-1]
                columns=df[[lastcolname]]
                rowwithNAN = len(df[df[lastcolname].isna()])
                length=len(df[[lastcolname]])
                length=length-rowwithNAN
                addition=df[[lastcolname]].sum()
                average=addition/length

                url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/ESTAT/{datasetcode}"


                resp = requests.get(url)

                #print(resp)
                root = ET.fromstring(resp.content)

                global update_data
                # Extract the metadata fields you are interested in
                for annotation in root.findall(".//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}Annotation"):
                    if annotation.find("{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}AnnotationType").text == "UPDATE_DATA":
                        update_data = annotation.find("{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}AnnotationTitle").text
                        print("UPDATE_DATA:",update_data)
                        
                instance=Rows(
                Tables=Tabless.objects.get(name=strreplace),
                Teilindikator=strreplaceTelli,
                Datenquelle=request.POST.get('Datenquelle'),
                Code=request.POST.get('datasetcode'),
                Datum=update_data,
                Wert=filteredATLastcolumn,
                Top3=topavg,
                EUDurchschnitt=average
                )
                instance.save()
        except Exception:
                print("Exception")
                instance=Rows(
                Tables=Tabless.objects.get(name=strreplace),
                Teilindikator=strreplaceTelli,
                Datenquelle=request.POST.get('Datenquelle'),
                Code=request.POST.get('datasetcode'),
                Datum=None,
                Wert=None,
                Top3=None,
                EUDurchschnitt=None
                )
                instance.save()
        
    return redirect(dashpage)

def dashpage(request):
    tables=Tabless.objects.all()
    for tab in tables:
        tab.name=tab.name.replace("_"," ")
    result=Rows.objects.all()
    for res in result:
        res.Teilindikator=res.Teilindikator.replace("_"," ")
    return render(request,'home/Krieslaufwirtschaft.html',{"tables":tables, "result":result,"i":0})

def editTable(request):
    if request.method=="POST":
        strreplace=request.POST.get('tablenewname').replace(" ","_")
        tab=Tabless(
            name=strreplace
        )
        tab.save()
        if(Rows.objects.filter(Tables=request.POST.get('tableoldname'))).exists():
            strreplacerow=request.POST.get('tableoldname').replace(" ","_")
            Row=Rows.objects.get(Tables=strreplacerow)
            Row.Tables=Tabless.objects.get(name=strreplace)
            Row.save()
        strreplaceold=request.POST.get('tableoldname').replace(" ","_")
        print(strreplaceold)
        oldTable=Tabless.objects.get(name=strreplaceold)
        oldTable.delete()
    return redirect(dashpage)

def editrows(request):
    print(request.POST.get('Datum'))
    if request.method=="POST":
        stringswithoutspaces=request.POST.get('Teilindikator').replace(" ","_")
        instance=Rows.objects.get(id=request.POST.get('recordid'))
        instance.Teilindikator=stringswithoutspaces
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

def deletetable(request):
    if request.method=="POST":
        strreplacerow=request.POST.get('tableoldname').replace(" ","_")
        print(strreplacerow)
        instance=Tabless.objects.get(name=strreplacerow)
        instance.delete()
    return redirect(dashpage)

def displaydata(request,slug):
    tables=Tabless.objects.all()
    for tab in tables:
        tab.name=tab.name.replace("_"," ")
    result=Rows.objects.all()
    for res in result:
        res.Teilindikator=res.Teilindikator.replace("_"," ")
    try:
            data = eurostat.get_data_df(slug)
            if data.empty:
                print('Data not available')
                redirect(dashpage)
            else:
                 tableHtml=data.to_html(classes='table table-stripped')
                
    except Exception:
                print("Exception")

    async def main():

            with open('templates/home/table.html', 'w') as file_handler:
                file_handler.writelines("{% extends 'home/Krieslaufwirtschaft.html' %}\n{% block table %}\n")

            with open('templates/home/table.html', 'a', encoding='utf-8') as file_handler:
                file_handler.writelines(tableHtml)

            # with open('templates/home/table.html', 'a', encoding='utf-8') as file_handler:
            #     file_handler.writelines("<script>$(document).ready(function(){$('#dataoftable').modal('show');});</script>")

            with open('templates/home/table.html', 'a') as file_handler:
                file_handler.writelines("{% endblock %}")
                await asyncio.sleep(1.2)

    asyncio.run(main())
    print("fdjasdlgjdflgldfdk")
    return render(request,'home/table.html',{"tables":tables, "result":result,"i":0,"checking":"yes"})