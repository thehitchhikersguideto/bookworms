from faker import Faker
import random
import csv
import pandas as pd
import random 
import numpy as np

faker = Faker()

raw_data = pd.read_csv('/Users/vera/Courses/projectReco/data/megaGymDataset.csv')

# List of possible exercise names
exercise_names = raw_data['Type'].unique()

# List of user IDs
user_ids = [faker.uuid4() for i in range(100)]

# Generate a list of users with age and gender
users = []
for i in range(100):
    age = random.randint(18, 65)
    gender = random.choice([True, False])
    user = {
        'id': faker.uuid4(),
        'age': age,
        'gender': gender
    }
    users.append(user)

# Generate 3000 rows of data
data = []
rated_exercises_by_user = {}
for i in range(3000):
    # Randomly select a user
    user = random.choice(users)

    # Randomly select an exercise that hasn't been rated by this user before
    rated_exercises = rated_exercises_by_user.get(user['id'], set())
    remaining_exercises = set(exercise_names) - rated_exercises
    if len(remaining_exercises) == 0:
        # This user has rated all the exercises
        continue
    exercise = random.choice(list(remaining_exercises))

    # Generate a random rating between 1 and 5
    # with a favorability towards 0  so that there are more 0s than other numbers
    
    if random.randint(0, 1) < 0.7: 
        rating = 0

    else:
        rating = random.randint(1, 5)


    # Add this exercise to the set of exercises rated by this user
    rated_exercises.add(exercise)
    rated_exercises_by_user[user['id']] = rated_exercises

  

    # Append the data to the list
    data.append((user['id'], user['age'], user['gender'], exercise, rating))
    
        
    

# Write the data to a CSV file
with open('user_rating_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['User ID', 'Age', 'Gender', 'Exercise', 'Rating'])
    for row in data:
        writer.writerow(row)