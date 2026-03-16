models:


workouts:
id
date
notes

exercises:
id
name

muscle_groups:
id
name

exercises_muscle_groups:
id
exercise_id
muscle_group_id

workouts_exercises:
id
workout_id
exercise_id
order

sets:
id
workout_exercise_id
set_number
reps
weight


