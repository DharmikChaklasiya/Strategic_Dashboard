import asyncio
import datetime
from django.shortcuts import render
from .models import Tabless
from .models import Rows
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import eurostat
import requests
from django.contrib import messages
import pandas as pd
import xml.etree.ElementTree as ET
from lxml import etree
import pycountry
import plotly.graph_objs as go


@login_required(login_url='/')
def index(request):
    return render(request, 'home/index.html')


def addTable(request):
    # To add a new Table
    if request.method == "POST":
        strTable = request.POST.get('tablename').replace(" ", "_")
        instance = Tabless(
            name=strTable
        )
        instance.save()
    return redirect(dashpage)

# Get the EU average value for the latest year
def eu_average(df):
    eu_average = df.iloc[:, 1:-1].mean()
    # Get the EU average value for the latest year
    eu_latest_average = eu_average.iloc[-1]
    return eu_latest_average

#to get the average of top3 contries
def top3average(df):
    # Get the top 3 countries by average recycling rate
    top_3 = df.nlargest(3, 'average')
    top_3_average = top_3.iloc[:, 1:-1].mean()
    # Calculate the average recycling rate for the top 3 countries for each year (2012-2021)
    top_3_latest_average = top_3_average.iloc[-1]
    return top_3_latest_average

def ATvalue(df,str):
    if(str=='Eurostat'):
        austria_latest_value = df.loc[df['countries'] == 'AT'].iloc[:, -2].values[0]
    elif(str=='WorldBank'):
        austria_latest_value = df.loc[df['Country'] == 'Austria'].iloc[:, -2].values[0]
    else:
        austria_latest_value = df.loc[df['country'] == 'Austria'].iloc[:, -2].values[0]

    return austria_latest_value


def queryDatagram(datacode,str):
    if(str=='Eurostat'):
        data = eurostat.get_data_df(datacode)
        european_countries = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]

        # Filter the DataFrame to only include European countries
        df = pd.DataFrame(data[data['geo\TIME_PERIOD'].isin(european_countries)])

        # Rename the column
        df = df.rename(columns={'geo\\TIME_PERIOD': 'countries'})

        # Drop the unwanted columns
        df = df.drop(columns=df.columns[:df.columns.get_loc('countries')])

        #adding additional average column with mean value of each row.
        df['average'] = df.iloc[:, 1:-1].mean(axis=1)

        return df
    elif(str=='WorldBank'):
        api_url = f"https://api.worldbank.org/v2/countries/all/indicators/{datacode}?format=json&per_page=20000"

        # Send a request to the World Bank API and get the response data
        response = requests.get(api_url)
        data = response.json()[1]
        metadata = response.json()[0]

        # Convert the response data to a pandas DataFrame and process it
        df = pd.json_normalize(data)
        df = df[['country.value', 'date', 'value']]
        df.columns = ['Country', 'Year', 'Value']
        df.dropna(inplace=True)
        countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
                    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", 
                    "Luxembourg", "Malta","Netherlands", "Poland",  "Portugal", "Romania", "Slovakia", "Slovenia",
                    "Spain", "Sweden"]
        df = df[df['Country'].isin(countries)]
        df['Year'] = pd.to_datetime(df['Year']).dt.year.astype(int)
        df = df.sort_values(['Country', 'Year'], ascending=[True, False])
        df['Value'] = df['Value'].round(1)
        df = df.pivot(index='Country', columns='Year', values='Value')
        df = df.reset_index()
        df.columns.name = None
        cols_to_drop = df.loc[:, df.columns[1]:2009].columns
        df = df.drop(columns=cols_to_drop)
        df['average'] = df.iloc[:, 1:-1].mean(axis=1)
        return df
    else:
        countries = "AUT+BEL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+IRL+ITA+LVA+LTU+LUX+NLD+NOR+POL+PRT+SVK+SVN+ESP+SWE+CHE+TUR+GBR"
        url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/{datacode}/{countries}.RECYCLING/all?startTime=2015&endTime=2021"

        # Send the request to the API
        response = requests.get(url)
        nsmap = {'generic': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic',
                'common': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'message': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message'}

        data1 = response.content.decode("utf-8-sig")
        root = etree.fromstring(data1)

        # Extract the necessary data from the ElementTree object
        data = []
        for series in root.findall(".//generic:Series", namespaces=nsmap):
            country_code = series.find(".//generic:Value[@concept='COU']", namespaces=nsmap).get("value")
            country_name = pycountry.countries.get(alpha_3=country_code).name
            year = []
            value = []
            for obs in series.findall(".//generic:Obs", namespaces=nsmap):
                year.append(obs.find("generic:Time", namespaces=nsmap).text)
                value.append(obs.find("generic:ObsValue", namespaces=nsmap).get("value"))
            data.append({"country": country_name, "year": year, "value": value})

        # Convert the extracted data to a pandas DataFrame
        df = pd.DataFrame()
        for d in data:
            country = d['country']
            years = d['year']
            values = d['value']
            # create a temporary data frame with the values for this dictionary
            temp_df = pd.DataFrame({'country': [country], **{years[i]: [float(values[i])] for i in range(len(years))}})
            # append the temporary data frame to the main data frame
            df = pd.concat([df, temp_df])
        # reset the index and print the resulting data frame
        df = df.reset_index(drop=True)
        
        # Calculate the average for each country
        df['average'] = df.iloc[:, 1:-1].mean(axis=1)

        return df

def updateddate(datasetcode,str):
    if(str=='Eurostat'):
        # To find the latest updated date
                url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/dataflow/ESTAT/{datasetcode}"
                resp = requests.get(url)
                root = ET.fromstring(resp.content)
                global update_data
                # Extract the metadata fields you are interested in
                for annotation in root.findall(
                        ".//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}Annotation"):
                    if annotation.find(
                            "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}AnnotationType").text == "UPDATE_DATA":
                        update_data = annotation.find(
                            "{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common}AnnotationTitle").text
                        update_data = update_data.split("T")
                        update_data = update_data[0]
                        return update_data
    elif(str=='WorldBank'):
        api_url = f"https://api.worldbank.org/v2/countries/all/indicators/{datasetcode}?format=json&per_page=20000"

        # Send a request to the World Bank API and get the response data
        response = requests.get(api_url)
        data = response.json()[1]
        metadata = response.json()[0]
        update_data=metadata['lastupdated']
        return update_data
    else:
        countries = "AUT+BEL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+IRL+ITA+LVA+LTU+LUX+NLD+NOR+POL+PRT+SVK+SVN+ESP+SWE+CHE+TUR+GBR"
        url = f"https://stats.oecd.org/restsdmx/sdmx.ashx/GetData/{datasetcode}/{countries}.RECYCLING/all?startTime=2015&endTime=2021"

        # Send the request to the API
        response = requests.get(url)

        nsmap = {'generic': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic',
                'common': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/common',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'message': 'http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message'}

        data1 = response.content.decode("utf-8-sig")
        root = etree.fromstring(data1)
        dataset_date = root.find(".//message:Prepared", namespaces=nsmap).text
        update_data = dataset_date.split("T")
        update_data = update_data[0]
        return update_data


def add(request, strreplace, strreplaceTelli, datasetcode, id):
    strreplace = str(strreplace)
    strreplace = strreplace.replace(' ', '_')
    # For editing or adding a row in a table
    try:
                df=queryDatagram(datasetcode,request.POST.get('Datenquelle'))
                filteredATLastcolumn=ATvalue(df,request.POST.get('Datenquelle'))
                topavg=top3average(df)
                average=eu_average(df)
                update_data=updateddate(datasetcode,request.POST.get('Datenquelle'))
                if id == None:
                    instance = Rows(
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
                else:
                    instance = Rows.objects.get(id=id)
                    instance.Tables = Tabless.objects.get(name=strreplace)
                    instance.Teilindikator = strreplaceTelli
                    instance.Datenquelle = request.POST.get('Datenquelle')
                    instance.Code = datasetcode
                    instance.Status="Active"
                    instance.Datum = update_data
                    instance.Wert = filteredATLastcolumn
                    instance.Top3 = topavg
                    instance.EUDurchschnitt = average
                    instance.save()
                messages.success(request, "Record added successfully.")
    except Exception:
            print("Exception")
            messages.error(request, "Data Not available OR Invalid Input")


def addRows(request):
    if request.method == "POST":
        strreplace = request.POST.get('tablee')
        strreplaceTelli = request.POST.get('Teilindikator')
        datasetcode = request.POST.get('datasetcode')
        id = None
        # Calling the function that will take the data and add to database
        add(request, strreplace, strreplaceTelli, datasetcode, id)

    return redirect(dashpage)

def showfig(austria,EU_average,top_3_average):
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(x=austria.index, y=austria.values.flatten(),
                                        mode='lines+markers',
                                        name='Austria (AT)'))

                    fig.add_trace(go.Scatter(x=EU_average.index, y=EU_average.values,
                                        mode='lines+markers',
                                        name='EU Average'))

                    fig.add_trace(go.Scatter(x=top_3_average.index, y=top_3_average.values,
                                        mode='lines+markers',
                                        name='Top 3 Countries Average'))

                    # Add labels, legend, and title to the chart
                    fig.update_layout(
                        title='Austria, EU Average, and Top 3 Countries',
                        xaxis_title='Year',
                        yaxis_title='value'
                    )

                    # Display the chart
                    fig.show()

def Plotparameters(df,str):
                    top_3 = df.nlargest(3, 'average')

                    # Calculate the average recycling rate for the top 3 countries for each year (2012-2021)
                    top_3_average = top_3.iloc[:, 1:-1].mean()

                    # Get Austria's recycling rate for each year (2012-2021)
                    if(str=='Eurostat'):
                        austria = df.loc[df['countries'] == 'AT'].iloc[:, 1:-1].transpose()
                    elif(str=='WorldBank'):
                         austria = df.loc[df['Country'] == 'Austria'].iloc[:, 1:-1].transpose()
                    else:
                         austria = df.loc[df['country'] == 'Austria'].iloc[:, 1:-1].transpose()
                    eu_average = df.iloc[:, 1:-1].mean()
                    return top_3_average,austria,eu_average


def dashpage(request):
    global fig
    fig=''
    global column_headers
    column_headers=''
    top3values=[]
    ATcolumn=[]
    EUaverage=[] 
    tables = Tabless.objects.all()
    for tab in tables:
        tab.name = tab.name.replace("_", " ")
    result = Rows.objects.all()
    checking="NO"
    if request.method=="POST":
        recordCode = request.POST.get('recordCode')
        recordDatenquelle = request.POST.get('recordDatenquelle')
        if(recordDatenquelle=='Eurostat'):
                    
            df=queryDatagram(recordCode,recordDatenquelle)
            # Get the top 3 countries by average recycling rate
            top_3_average,austria,eu_average=Plotparameters(df,recordDatenquelle)

                        ######################################## Plotly ########################################
            showfig(austria,eu_average,top_3_average)

        elif(recordDatenquelle=='WorldBank'):
            df=queryDatagram(recordCode,recordDatenquelle)

            top_3_average,austria,eu_average=Plotparameters(df,recordDatenquelle)

            showfig(austria,eu_average,top_3_average)
            ######################################## Plotly ########################################


        else:
            df=queryDatagram(recordCode,recordDatenquelle)


            top_3_average,austria,eu_average=Plotparameters(df,recordDatenquelle)

            ######################################## Plotly ########################################
            showfig(austria,eu_average,top_3_average)


    return render(request, 'home/Krieslaufwirtschaft.html', {"tables": tables, "result": result, "i": 0, "Heads":column_headers,"top3":top3values,"average":EUaverage,"ATcolumn":ATcolumn,"checking":checking,"fig":fig})


def editTable(request):
    # Editing the base table
    if request.method == "POST":
        old_name = request.POST.get('tableoldname').replace(" ", "_")
        new_name = request.POST.get('tablenewname').replace(" ", "_")

        try:
            # Update the existing Tabless instance
            table = Tabless.objects.get(name=old_name)
            table.name = new_name
            table.save()

            # Update the Rows instances associated with the updated Tabless instance
            Rows.objects.filter(Tables__name=old_name).update(Tables=table)

        except Tabless.DoesNotExist:
            pass

    return redirect(dashpage)


def editrows(request):
    if request.method == "POST":
        id = request.POST.get('recordid')
        strreplace = request.POST.get('tablee')
        strreplaceTelli = request.POST.get('Teilindikator')
        datasetcode = request.POST.get('Code')
        # calling a function to edit rows
        add(request, strreplace, strreplaceTelli, datasetcode, id)
    return redirect(dashpage)


def deleterows(request):
    if request.method == "POST":
        # to delete a given row
        instance = Rows.objects.get(id=request.POST.get('recordid'))
        instance.delete()
    return redirect(dashpage)


def deletetable(request):
    if request.method == "POST":
        # to delete a given row
        strreplacerow = request.POST.get('tableoldname').replace(" ", "_")
        instance = Tabless.objects.get(name=strreplacerow)
        instance.delete()
    return redirect(dashpage)


def displaydata(request, str, type):
    # to display the data in tabular format on clicking the view icon
    tables = Tabless.objects.all()
    for tab in tables:
        tab.name = tab.name.replace("_", " ")
    result = Rows.objects.all()
    for res in result:
        res.Teilindikator = res.Teilindikator.replace("_", " ")

    data=queryDatagram(str,type)
    tableHtml = data.to_html(classes='table table-stripped text-secondary')

    async def main():
        # Appending the HTML table to new file
        with open('templates/home/table.html', 'w') as file_handler:
            file_handler.writelines("{% extends 'home/Krieslaufwirtschaft.html' %}\n{% block table %}\n")

        with open('templates/home/table.html', 'a', encoding='utf-8') as file_handler:
            file_handler.writelines(tableHtml)

        with open('templates/home/table.html', 'a') as file_handler:
            file_handler.writelines("{% endblock %}")

    asyncio.run(main())
    return render(request, 'home/table.html', {"tables": tables, "result": result, "i": 0, "checking": "yes"})


def check_update(request):
    if request.method == "POST":
        id = request.POST.get('recordid')
        datasetcode = request.POST.get('Code')
        res = Rows.objects.get(id=id)
        if (request.POST.get('Datenquelle') == "Eurostat"):
            update_data=updateddate(datasetcode,request.POST.get('Datenquelle'))
            # if the date in database and updated data date is different
            if str(update_data) != str(res.Datum) and res.Datenquelle == "Eurostat":
                res.Status = "Update available"
                res.save()
                messages.warning(request, "Update available.")
        elif (request.POST.get('Datenquelle') == "WorldBank"):
            update_data=updateddate(datasetcode,request.POST.get('Datenquelle'))
            # if the date in database and updated data date is different
            if str(update_data) != str(res.Datum) and res.Datenquelle == "WorldBank":
                res.Status = "Update available"
                res.save()
                messages.warning(request, "Update available.")
        elif (request.POST.get('Datenquelle') == "OECD"):
            update_data=updateddate(datasetcode,request.POST.get('Datenquelle'))

            # if the date in database and updated data date is different
            if str(update_data) != str(res.Datum) and res.Datenquelle == "OECD":
                res.Status = "Update available"
                res.save()
                messages.warning(request, "Update available.")
    return redirect(dashpage)