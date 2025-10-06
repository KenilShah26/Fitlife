from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Workout, Exercise, ExerciseSet, WorkoutPlan, PlanDay, PlanExercise, Goal, BMIRecord
from .forms import ExerciseForm, SetForm, LoginForm, RegisterForm, BMICalculatorForm
import json
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import models


@login_required
def log_workout(request):
    # Get or create today's workout
    today = timezone.now().date()
    workout, created = Workout.objects.get_or_create(
        user=request.user,
        date=today
    )
    
    form = ExerciseForm()
    
    if request.method == 'POST':
        if 'add_exercise' in request.POST:
            return add_exercise(request, workout)
        elif 'delete_exercise' in request.POST:
            return delete_exercise(request)
    
    # Get today's exercises
    exercises = workout.exercises.all().prefetch_related('sets')
    
    context = {
        'form': form,
        'workout': workout,
        'exercises': exercises,
        'range': range(1, 9), 
    }
    
    return render(request, 'workouts/log_workout.html', context)

@login_required
def add_exercise(request, workout):
    exercise_name = request.POST.get('exercise_name', '').strip()
    sets_count = request.POST.get('sets_count')
    
    if not exercise_name:
        messages.error(request, 'Please enter an exercise name')
        return redirect('log_workout')
    
    if not sets_count or int(sets_count) < 1:
        messages.error(request, 'Please select number of sets')
        return redirect('log_workout')
    
    sets_count = int(sets_count)
    
    # Validate all set data
    sets_data = []
    for i in range(1, sets_count + 1):
        reps = request.POST.get(f'reps_{i}')
        weight = request.POST.get(f'weight_{i}')
        
        if not reps or not weight:
            messages.error(request, f'Please fill in reps and weight for Set {i}')
            return redirect('log_workout')
        
        try:
            reps = int(reps)
            weight = float(weight)
            
            if reps < 1 or weight < 0:
                raise ValueError
                
            sets_data.append({'reps': reps, 'weight': weight})
        except ValueError:
            messages.error(request, f'Invalid reps or weight for Set {i}')
            return redirect('log_workout')
    
    # Create exercise
    exercise = Exercise.objects.create(
        workout=workout,
        name=exercise_name
    )
    
    # Create sets
    for i, set_data in enumerate(sets_data, 1):
        ExerciseSet.objects.create(
            exercise=exercise,
            set_number=i,
            reps=set_data['reps'],
            weight=set_data['weight']
        )
    
    messages.success(request, f'Added {exercise_name} to workout')
    return redirect('log_workout')

@login_required
def delete_exercise(request):
    exercise_id = request.POST.get('exercise_id')
    if exercise_id:
        try:
            exercise = get_object_or_404(Exercise, id=exercise_id, workout__user=request.user)
            exercise_name = exercise.name
            exercise.delete()
            messages.success(request, f'Deleted {exercise_name} from workout')
        except Exercise.DoesNotExist:
            messages.error(request, 'Exercise not found')
    
    return redirect('log_workout')

# AJAX view for dynamic set inputs
@login_required
def get_set_inputs(request):
    sets_count = request.GET.get('sets_count', 0)
    try:
        sets_count = int(sets_count)
        if sets_count < 1 or sets_count > 8:
            return JsonResponse({'error': 'Invalid sets count'})
    except ValueError:
        return JsonResponse({'error': 'Invalid sets count'})
    
    html = ''
    for i in range(1, sets_count + 1):
        html += f'''
        <div class="set-group">
            <div class="set-title">Set {i}</div>
            <div class="set-row">
                <input type="number" 
                       name="reps_{i}" 
                       class="set-input" 
                       placeholder="Reps" 
                       min="1"
                       required>
                <input type="number" 
                       name="weight_{i}" 
                       class="set-input" 
                       placeholder="Weight (kg)" 
                       min="0" 
                       step="0.5"
                       required>
            </div>
        </div>
        '''
    
    return JsonResponse({'html': html})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name']
            )
            login(request, user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



@login_required
def workout_plans(request):
    """Display all workout plans"""
    plans = WorkoutPlan.objects.all()
    return render(request, 'workouts/plans.html', {'plans': plans})

@login_required
def plan_exercises(request, day_id):
    """Get exercises for a specific plan day"""
    day = get_object_or_404(PlanDay, id=day_id)
    exercises = day.exercises.all()
    return render(request, 'workouts/exercises.html', {
        'day': day,
        'exercises': exercises
    })

@login_required
def start_workout(request, day_id):
    """Start a workout based on a plan day"""
    day = get_object_or_404(PlanDay, id=day_id)
    exercises = day.exercises.all()
    
    if request.method == 'POST':
        # Create new workout
        workout = Workout.objects.create(user=request.user)
        
        # Process each exercise
        for plan_exercise in exercises:
            # Get number of sets for this exercise
            sets_count = int(request.POST.get(f'sets_{plan_exercise.id}', 0))
            
            if sets_count > 0:
                # Create exercise record
                exercise = Exercise.objects.create(
                    workout=workout,
                    name=plan_exercise.name
                )
                
                # Create sets
                for set_num in range(1, sets_count + 1):
                    reps = request.POST.get(f'reps_{plan_exercise.id}_{set_num}')
                    weight = request.POST.get(f'weight_{plan_exercise.id}_{set_num}')
                    
                    if reps and weight:
                        ExerciseSet.objects.create(
                            exercise=exercise,
                            set_number=set_num,
                            reps=int(reps),
                            weight=float(weight)
                        )
        
        messages.success(request, 'Workout saved successfully!')
        return redirect('workout_plans')
    
    return render(request, 'workouts/start_workout.html', {
        'day': day,
        'exercises': exercises
    })

@login_required
def workout_history(request):
    """Display user's workout history"""
    workouts = Workout.objects.filter(user=request.user).prefetch_related('exercises__sets')
    return render(request, 'workouts/history.html', {'workouts': workouts})

@login_required
def progress_tracking(request):
    """Display progress tracking with charts"""
    # Get all unique exercises for the user
    user_exercises = Exercise.objects.filter(
        workout__user=request.user
    ).values_list('name', flat=True).distinct().order_by('name')
    
    selected_exercise = request.GET.get('exercise')
    chart_data = []
    
    if selected_exercise and selected_exercise in user_exercises:
        # Get workout data for selected exercise
        exercises = Exercise.objects.filter(
            workout__user=request.user,
            name=selected_exercise
        ).prefetch_related('sets', 'workout').order_by('workout__date')
        
        # Calculate max weight for each workout date
        workout_data = {}
        for exercise in exercises:
            date = exercise.workout.date
            max_weight = exercise.sets.aggregate(
                max_weight=models.Max('weight')
            )['max_weight']
            
            if max_weight and (date not in workout_data or max_weight > workout_data[date]):
                workout_data[date] = max_weight
        
        # Convert to chart format
        chart_data = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'weight': float(weight)
            }
            for date, weight in sorted(workout_data.items())
        ]
    
    return render(request, 'workouts/progress.html', {
        'exercises': user_exercises,
        'selected_exercise': selected_exercise,
        'chart_data': chart_data
    })


@login_required
def fitness_goals(request):
    """Display user's fitness goals"""
    goals = Goal.objects.filter(user=request.user)
    return render(request, 'workouts/goals.html', {'goals': goals})

@login_required
def add_goal(request):
    """Add a new fitness goal"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        goal_type = request.POST.get('goal_type')
        target_value = request.POST.get('target_value')
        current_value = request.POST.get('current_value', 0)
        unit = request.POST.get('unit')
        deadline = request.POST.get('deadline')
        
        if title and target_value and unit:
            goal = Goal.objects.create(
                user=request.user,
                title=title,
                description=description,
                goal_type=goal_type,
                target_value=float(target_value),
                current_value=float(current_value),
                unit=unit,
                deadline=deadline if deadline else None
            )
            messages.success(request, f'Goal "{title}" added successfully!')
            return redirect('fitness_goals')
        else:
            messages.error(request, 'Please fill all required fields.')
    
    return render(request, 'workouts/add_goal.html')

@login_required
def update_goal_progress(request, goal_id):
    """Update progress for a specific goal"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        current_value = request.POST.get('current_value')
        if current_value:
            goal.current_value = float(current_value)
            
            # Check if goal is completed
            if goal.current_value >= goal.target_value:
                goal.status = 'completed'
            
            goal.save()
            messages.success(request, f'Progress updated for "{goal.title}"!')
        else:
            messages.error(request, 'Please enter a valid progress value.')
    
    return redirect('fitness_goals')

@login_required
def delete_goal(request, goal_id):
    """Delete a fitness goal"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    goal_title = goal.title
    goal.delete()

    return redirect('fitness_goals')

@login_required
def dashboard(request):
    user = request.user

    context = {
        'user': user,
    }
    return render(request, 'workouts/dashboard.html', context)



@login_required
def bmi_calculator(request):
    form = BMICalculatorForm()
    bmi_result = None
    
    if request.method == 'POST':
        form = BMICalculatorForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            height = form.cleaned_data['height']
            
            # Convert height from cm to meters
            height_m = height / 100
            
            # Calculate BMI
            bmi = weight / (height_m * height_m)
            
            # Save BMI record
            bmi_record = form.save(commit=False)
            bmi_record.user = request.user
            bmi_record.bmi = round(bmi, 1)
            bmi_record.save()
            
            bmi_result = {
                'bmi': round(bmi, 1),
                'weight': weight,
                'height': height,
                'category': bmi_record.bmi_category
            }
    
    context = {
        'form': form,
        'bmi_result': bmi_result,
        'active_tab': 'calculator'
    }
    return render(request, 'workouts/bmi_calculator.html', context)

@login_required
def bmi_history(request):
    bmi_records = BMIRecord.objects.filter(user=request.user)
    
    context = {
        'bmi_records': bmi_records,
        'active_tab': 'history'
    }
    return render(request, 'workouts/bmi_calculator.html', context)

@login_required
def bmi_learn_more(request):
    context = {
        'active_tab': 'learn_more'
    }
    return render(request, 'workouts/bmi_calculator.html', context)

@login_required
def clear_bmi_history(request):
    if request.method == 'POST':
        BMIRecord.objects.filter(user=request.user).delete()
        messages.success(request, 'BMI history cleared successfully.')
    return redirect('bmi_history')

# Add these new views to your existing views.py file

from .forms import WorkoutPlanForm, PlanDayForm

@login_required
def create_workout_plan(request):
    """Create a new workout plan"""
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name', '').strip()
        plan_description = request.POST.get('plan_description', '').strip()
        
        if not plan_name:
            messages.error(request, 'Please enter a plan name')
            return render(request, 'workouts/create_plan.html')
        
        # Create the workout plan
        plan = WorkoutPlan.objects.create(
            name=plan_name,
            description=plan_description
        )
        
        # Process each day
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        order = 1
        
        for day in days_of_week:
            is_rest_day = request.POST.get(f'{day}_rest') == 'on'
            day_name = request.POST.get(f'{day}_name', '').strip()
            
            if not is_rest_day and day_name:
                # Create plan day
                plan_day = PlanDay.objects.create(
                    plan=plan,
                    name=day_name,
                    order=order
                )
                
                # Get exercises for this day
                exercise_names = request.POST.getlist(f'{day}_exercises[]')
                exercise_order = 1
                
                for exercise_name in exercise_names:
                    exercise_name = exercise_name.strip()
                    if exercise_name:
                        PlanExercise.objects.create(
                            day=plan_day,
                            name=exercise_name,
                            order=exercise_order
                        )
                        exercise_order += 1
                
                order += 1
        
        messages.success(request, f'Workout plan "{plan_name}" created successfully!')
        return redirect('workout_plans')
    
    return render(request, 'workouts/create_plan.html')

@login_required
def update_workout_plan(request, plan_id):
    """Update an existing workout plan"""
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    
    if request.method == 'POST':
        plan_name = request.POST.get('plan_name', '').strip()
        plan_description = request.POST.get('plan_description', '').strip()
        
        if not plan_name:
            messages.error(request, 'Please enter a plan name')
            return render(request, 'workouts/update_plan.html', {'plan': plan})
        
        # Update the workout plan
        plan.name = plan_name
        plan.description = plan_description
        plan.save()
        
        # Delete existing days and recreate
        plan.days.all().delete()
        
        # Process each day (same logic as create)
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        order = 1
        
        for day in days_of_week:
            is_rest_day = request.POST.get(f'{day}_rest') == 'on'
            day_name = request.POST.get(f'{day}_name', '').strip()
            
            if not is_rest_day and day_name:
                plan_day = PlanDay.objects.create(
                    plan=plan,
                    name=day_name,
                    order=order
                )
                
                exercise_names = request.POST.getlist(f'{day}_exercises[]')
                exercise_order = 1
                
                for exercise_name in exercise_names:
                    exercise_name = exercise_name.strip()
                    if exercise_name:
                        PlanExercise.objects.create(
                            day=plan_day,
                            name=exercise_name,
                            order=exercise_order
                        )
                        exercise_order += 1
                
                order += 1
        
        messages.success(request, f'Workout plan "{plan_name}" updated successfully!')
        return redirect('workout_plans')
    
    # Get existing data for form
    existing_days = {}
    for day in plan.days.all():
        # Extract day from name (assuming format like "Monday: Push Day")
        day_part = day.name.split(':')[0].strip().lower()
        existing_days[day_part] = {
            'name': day.name,
            'exercises': [exercise.name for exercise in day.exercises.all()]
        }
    
    context = {
        'plan': plan,
        'existing_days': existing_days
    }
    return render(request, 'workouts/update_plan.html', context)

@login_required
def delete_workout_plan(request, plan_id):
    """Delete a workout plan"""
    plan = get_object_or_404(WorkoutPlan, id=plan_id)
    plan_name = plan.name
    plan.delete()
    messages.success(request, f'Workout plan "{plan_name}" deleted successfully!')
    return redirect('workout_plans')

def custom_logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  