from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('call-logs/', views.call_logs_list, name='call_logs'),
    path('chat/', views.chat, name='chat'),
    path('knowledge-graph/', views.knowledge_graph, name='knowledge_graph'),
    path('upload-transcript/', views.upload_transcript, name='upload_transcript'),
    path("chat_query/", views.chat_query, name="chat_query"),
    path("objections_summary/", views.objections_summary, name="objections_summary"),
]
