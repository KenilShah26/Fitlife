# Run this in Django shell: python manage.py shell
# Then: exec(open('populate_db.py').read())

from tracker.models import WorkoutPlan, PlanDay, PlanExercise

# Clear existing data (optional)
WorkoutPlan.objects.all().delete()

# Create Push Pull Legs (PPL) Plan
ppl_plan = WorkoutPlan.objects.create(
    name="Push Pull Legs (PPL)",
    description="A classic split routine focusing on different movement patterns."
)

# PPL Days
days_data = [
    ("Monday: Push Day", [
        "Bench Press", "Overhead Press", "Incline Dumbbell Press", 
        "Lateral Raises", "Tricep Dips", "Close-Grip Bench Press"
    ]),
    ("Tuesday: Pull Day", [
        "Pull-ups", "Barbell Rows", "Lat Pulldowns", 
        "Face Pulls", "Bicep Curls", "Hammer Curls"
    ]),
    ("Wednesday: Leg Day", [
        "Squats", "Romanian Deadlifts", "Bulgarian Split Squats", 
        "Leg Press", "Calf Raises", "Leg Curls"
    ]),
    ("Thursday: Rest", []),
    ("Friday: Push Day", [
        "Incline Barbell Press", "Dumbbell Shoulder Press", "Decline Press", 
        "Cable Lateral Raises", "Overhead Tricep Extension", "Diamond Push-ups"
    ]),
    ("Saturday: Pull Day", [
        "Deadlifts", "T-Bar Rows", "Cable Rows", 
        "Reverse Flyes", "Preacher Curls", "Cable Curls"
    ]),
    ("Sunday: Rest", [])
]

for i, (day_name, exercises) in enumerate(days_data, 1):
    day = PlanDay.objects.create(
        plan=ppl_plan,
        name=day_name,
        order=i
    )
    
    for j, exercise_name in enumerate(exercises, 1):
        PlanExercise.objects.create(
            day=day,
            name=exercise_name,
            order=j
        )

# Create Full Body Split Plan
fullbody_plan = WorkoutPlan.objects.create(
    name="Full Body Split",
    description="Hit every major muscle group in each session."
)

# Full Body Days
fullbody_days = [
    ("Workout A", [
        "Squats", "Bench Press", "Barbell Rows", 
        "Overhead Press", "Romanian Deadlifts", "Plank"
    ]),
    ("Workout B", [
        "Deadlifts", "Incline Dumbbell Press", "Pull-ups", 
        "Dumbbell Shoulder Press", "Lunges", "Russian Twists"
    ]),
    ("Workout C", [
        "Front Squats", "Dumbbell Bench Press", "T-Bar Rows", 
        "Lateral Raises", "Hip Thrusts", "Mountain Climbers"
    ])
]

for i, (day_name, exercises) in enumerate(fullbody_days, 1):
    day = PlanDay.objects.create(
        plan=fullbody_plan,
        name=day_name,
        order=i
    )
    
    for j, exercise_name in enumerate(exercises, 1):
        PlanExercise.objects.create(
            day=day,
            name=exercise_name,
            order=j
        )

print("Database populated successfully!")
print(f"Created {WorkoutPlan.objects.count()} workout plans")
print(f"Created {PlanDay.objects.count()} plan days")
print(f"Created {PlanExercise.objects.count()} plan exercises")