from django.core.management.base import BaseCommand
from django.conf import settings
from pymongo import MongoClient
from octofit_app.models import User, Team, Activity, Leaderboard, Workout
from octofit_tracker.test_data import get_test_data  # Исправленный импорт
from bson import ObjectId

class Command(BaseCommand):
    help = 'Populate the database with test data for users, teams, activities, leaderboard, and workouts'

    def handle(self, *args, **kwargs):
        # Подключение к MongoDB
        client = MongoClient(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['PORT'])
        db = client[settings.DATABASES['default']['NAME']]

        # Очистка коллекций
        db.users.drop()
        db.teams.drop()
        db.activity.drop()
        db.leaderboard.drop()
        db.workouts.drop()

        # Получение тестовых данных
        data = get_test_data()

        # Создание пользователей
        users = [User(**user) for user in data['users']]
        User.objects.bulk_create(users)

        # Создание команд и назначение участников
        teams = []
        for team_data in data['teams']:
            team = Team(_id=team_data['_id'], name=team_data['name'])
            team.save()
            for user in User.objects.all():
                team.members.add(user)  # Добавление каждого пользователя вручную
            teams.append(team)

        # Создание активностей
        for activity_data in data['activities']:
            user = User.objects.first()  # Получение первого пользователя
            if user:
                activity_data['user'] = user  # Назначение пользователя
                activity = Activity(**activity_data)
                activity.save()  # Сохранение каждого объекта отдельно

        # Создание записей таблицы лидеров
        leaderboard_entries = []
        for entry_data in data['leaderboard']:
            entry_data['user'] = User.objects.first()  # Назначение первого пользователя для простоты
            leaderboard_entries.append(Leaderboard(**entry_data))
        Leaderboard.objects.bulk_create(leaderboard_entries)

        # Создание тренировок
        workouts = [Workout(**workout) for workout in data['workouts']]
        Workout.objects.bulk_create(workouts)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with test data.'))
