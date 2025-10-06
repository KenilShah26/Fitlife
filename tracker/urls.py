from django.urls import path
from . import views


urlpatterns = [
    path('log/', views.log_workout, name='log_workout'),
    path('get-set-inputs/', views.get_set_inputs, name='get_set_inputs'),
    path('',views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('workout-plans/', views.workout_plans, name='workout_plans'),
    path('workout-plans/create/', views.create_workout_plan, name='create_workout_plan'),
    path('workout-plans/update/<int:plan_id>/', views.update_workout_plan, name='update_workout_plan'),
    path('workout-plans/delete/<int:plan_id>/', views.delete_workout_plan, name='delete_workout_plan'),
    path('exercises/<int:day_id>/', views.plan_exercises, name='plan_exercises'),
    path('start/<int:day_id>/', views.start_workout, name='start_workout'),
    path('workout-history/', views.workout_history, name='workout_history'),
    path('progress/', views.progress_tracking, name='progress'),
    path('goals/', views.fitness_goals, name='fitness_goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/update/<int:goal_id>/', views.update_goal_progress, name='update_goal_progress'),
    path('goals/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bmi-calculator/', views.bmi_calculator, name='bmi_calculator'),
    path('bmi-history/', views.bmi_history, name='bmi_history'),
    path('bmi-learn-more/', views.bmi_learn_more, name='bmi_learn_more'),
    path('clear-bmi-history/', views.clear_bmi_history, name='clear_bmi_history'),
    path('logout/', views.custom_logout_view, name='logout')
    ]
