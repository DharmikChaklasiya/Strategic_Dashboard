from django.contrib import admin
from django.urls import path, include

import FTI_Monitor.views

urlpatterns = [
    path('', FTI_Monitor.views.index, name='dashboard'),
    path('Krieslaufwirtschaft',FTI_Monitor.views.dashpage,name='Krieslaufwirtschaft'),
    path('addTable',FTI_Monitor.views.addTable, name='addtable'),
    path('addRows',FTI_Monitor.views.addRows, name='addRows'),
    path('editTable',FTI_Monitor.views.editTable, name='editTable'),
    path('editrows',FTI_Monitor.views.editrows, name='editrows'),
    path('deleterows',FTI_Monitor.views.deleterows, name='deleterows'),
    path('deletetable',FTI_Monitor.views.deletetable, name='deletetable'),
    path('Krieslaufwirtschaft/<slug:slug>',FTI_Monitor.views.displaydata,name='displaydata')
]