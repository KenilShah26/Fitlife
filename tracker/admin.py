from django.contrib import admin
from .models import Workout, Exercise, ExerciseSet, WorkoutPlan, PlanDay, PlanExercise, Goal

admin.site.register(Workout)
admin.site.register(Exercise)   
admin.site.register(ExerciseSet)
admin.site.register(WorkoutPlan)
admin.site.register(PlanDay)    
admin.site.register(PlanExercise)
admin.site.register(Goal)
