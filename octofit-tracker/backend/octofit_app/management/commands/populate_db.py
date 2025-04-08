from django.core.management.base import BaseCommand
from octofit_app.models import User, Team, Activity, Leaderboard, Workout
from octofit_tracker.test_data import test_users, test_teams, test_activities, test_leaderboard, test_workouts
from bson import ObjectId
from datetime import timedelta
from pymongo import MongoClient
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activities, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        # Connect to MongoDB
        client = MongoClient(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['PORT'])
        db = client[settings.DATABASES['default']['NAME']]

        # Clear existing data
        db.users.delete_many({})
        db.teams.delete_many({})
        db.activity.delete_many({})
        db.leaderboard.delete_many({})
        db.workouts.delete_many({})

        # Populate users
        users = {}
        for user_data in test_users:
            user = User.objects.create(
                _id=ObjectId(),
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            users[user_data['username']] = user

        # Populate teams
        for team_data in test_teams:
            team = Team.objects.create(
                _id=ObjectId(),
                name=team_data['name']
            )
            for member_username in team_data['members']:
                team.members.add(users[member_username])

        # Populate activities
        for activity_data in test_activities:
            Activity.objects.create(
                _id=ObjectId(),
                user=users[activity_data['user']],
                activity_type=activity_data['activity_type'],
                duration=timedelta(hours=int(activity_data['duration'].split(':')[0]),
                                   minutes=int(activity_data['duration'].split(':')[1]))
            )

        # Populate leaderboard
        for leaderboard_data in test_leaderboard:
            Leaderboard.objects.create(
                _id=ObjectId(),
                user=users[leaderboard_data['user']],
                score=leaderboard_data['score']
            )

        # Populate workouts
        for workout_data in test_workouts:
            Workout.objects.create(
                _id=ObjectId(),
                name=workout_data['name'],
                description=workout_data['description']
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
