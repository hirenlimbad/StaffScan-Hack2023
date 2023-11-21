from django.contrib import admin
from django.urls import path
from myapp import views

from django.conf import settings
from django.conf.urls.static import static
from . import AttendanceMechanism
from . import employeeManagement
from user_panel import views as user_view

urlpatterns = [
    path('', views.login_view, name='login-page'),
    path('index.html', views.index, name='index'),
    path('addEmployee.html', views.add_employee, name= "add emoloyee"),
    path('showEmployee.html', views.employee_list, name= "show emoloyee"),
    path('get-latest-employee-data/', views.get_latest_employee_data, name='get_latest_employee_data'),
    path('deleteEmployee.html', views.delete_employee, name= "Delete Employee"),
    path('editEmployee.html', views.edit_employee, name="Edit Employee"),
    path('updatedEmployee', view=views.update_employee, name="Update Employee"),
    path('video_feed/', AttendanceMechanism.AttendanceMechanism().video_feed, name='video_feed'),
    path('cameraSetup.html/', views.actual_video_feed, name='actual_video_feed'),
    path('assignTask.html', views.assign_task, name='assign_task'),
    path('showTasks.html', views.show_assigned_tasks, name= "assigned_task_view"),
    path('assign_task/<int:employee_id>/<str:employee_name>/', views.assign_task, name='assign_task'),
    path('view_employee/<int:employee_id>/', views.view_employee, name='view_employee'),
    path('upload_csv/', employeeManagement.employeeManagement().upload_csv, name='upload_csv'),
    path('editEmployee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('assign_leave', views.assign_leave, name='assign_leave'),
    path('approve_leave/<int:employee_id>/', views.approve_leave, name='approve_leave'),
    path('late_employee', views.late_employee, name='late_employee'),
    # path('apply_penalty/', views.apply_penalty, name='apply_penalty'),
    path('apply_penalty/<int:employee_id>/', views.apply_penalty, name='apply_penalty'),
    path('set_timings.html', views.setTimings, name="SetTimings"),
    path('set-timings/', views.setTimings, name='set_timings'),
    path('dismiss_task/<str:employee_id>/<str:deadline>/<str:task_id>/', views.dismiss_task, name='dismiss_task'),





    # Employee dashboard.
    path('employee_login', user_view.admin_login, name="employee_login"),
    path('employee_dashboard', user_view.employee_dashboard, name="employee_dashboard"),
    path('punch/', user_view.punch, name='punch'),
    path('edit_employee/', user_view.edit_employee_data, name='edit_employee_data'),
    path('leave_request/', user_view.leave_request, name='leave_request'),
    path('download_attendance', user_view.download_attendance, name='download_attendance'),
    path('mark_task_completed/<int:employee_id>/<int:task_id>/', user_view.mark_task_completed, name='mark_task_completed'),
    path('mark_task_completed/<str:employee_id>/<str:task_id>/', user_view.mark_task_completed, name='strmark_task_completed'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)