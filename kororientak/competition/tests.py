import datetime

from django.http import parse_cookie
from django.test import TestCase, Client
from django.utils.timezone import get_current_timezone

from .models import Race, Category, Task, Player, Time


class RaceFlowTestCase(TestCase):
    def setUp(self) -> None:
        today = datetime.datetime.now(tz=get_current_timezone())

        self.race = Race.objects.create(name='KorOrienťák', start=today, end=today + datetime.timedelta(days=3))
        self.category_causual = Category.objects.create(name='Výletník', competitive=False, race=self.race)
        self.category_competitive = Category.objects.create(name='Borec', competitive=True, race=self.race)

        self.task_registration = Task.objects.create(
            name='Registrace',
            text='Napiš svoje jméno, vyber si kategorii a vyraž.',
            registration=True,
            race=self.race)
        self.task_finish = Task.objects.create(
            name='Cíl',
            text='Gratulujeme, jsi v cíli!',
            finish=True,
            race=self.race)

        # Text only
        self.task1 = Task.objects.create(
            name='Stanoviště 1',
            text='Splň úkol a můžeš pokračovat',
            race=self.race)

        # YouTube link only
        self.task2 = Task.objects.create(
            name='Stanoviště 2',
            youtube_link='https://youtu.be/VUaX77nCI2g',
            race=self.race)

        # Text and Youtube link
        self.task3 = Task.objects.create(
            name='Stanoviště 3',
            text='Splň úkol a můžeš pokračovat',
            youtube_link='https://youtu.be/VUaX77nCI2g',
            race=self.race)

        self.client = Client()

    def test_registration_open(self):
        response = self.client.get(f'/ukol/{self.task_registration.uuid}')
        self.assertEquals(response.status_code, 200)

        # We should have task but not player in the context
        self.assertEquals(response.context['task'], self.task_registration)
        self.assertIsNone(response.context['player'])

        # Test we can see registration data and categories
        self.assertContains(response, self.task_registration.name)
        self.assertContains(response, self.task_registration.text)
        self.assertContains(response, self.category_causual.name)
        self.assertContains(response, self.category_competitive.name)
        self.assertContains(response, 'Začít')

    def test_register_causual(self):
        player_name = 'Sokolík'
        response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': player_name,
            'category': self.category_causual.pk
        }, follow=True)
        self.assertEquals(response.status_code, 200)
        self._assert_correct_player_created(response, player_name, self.category_causual)

        # We should have task and player data with complete tasks in the context
        self.assertEquals(response.context['task'], self.task_registration)
        self.assertIsNotNone(response.context['player'])
        self.assertEquals(len(response.context['complete_tasks']), 3)
        self.assertEquals(response.context['complete_tasks_total_count'], 3)
        self.assertEquals(response.context['complete_tasks_complete_count'], 0)

        # Test we can see player name, category and complete tasks list
        self.assertContains(response, player_name)
        self.assertContains(response, self.category_causual.name)
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task2.name)
        self.assertContains(response, self.task3.name)

    def test_register_competitive(self):
        player_name = 'Velký Sokol'
        response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': player_name,
            'category': self.category_competitive.pk
        }, follow=True)
        self.assertEquals(response.status_code, 200)
        self._assert_correct_player_created(response, player_name, self.category_competitive)

        # We should have task and player data but not complete tasks in the context
        self.assertEquals(response.context['task'], self.task_registration)
        self.assertIsNotNone(response.context['player'])
        self.assertFalse('complete_tasks' in response.context)
        self.assertFalse('complete_tasks_total_count' in response.context)
        self.assertFalse('complete_tasks_complete_count' in response.context)

        # Test we can see player name and category but no complete tasks list
        self.assertContains(response, player_name)
        self.assertContains(response, self.category_competitive.name)
        self.assertNotContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)
        self.assertNotContains(response, self.task3.name)

    def test_task1_not_registered(self):
        response = self.client.get(f'/ukol/{self.task1.uuid}')
        self.assertEquals(response.status_code, 200)
        self._assert_no_player_data_set(response)

        # We should only have task data in context
        self.assertEquals(response.context['task'], self.task1)

        # Test we can see task details and some registration info
        self.assertContains(response, 'Pokud se chceš zúčastnit celého běhu')
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task1.text)

    def test_task2_not_registered(self):
        response = self.client.get(f'/ukol/{self.task2.uuid}')
        self.assertEquals(response.status_code, 200)
        self._assert_no_player_data_set(response)

        # We should only have task data in context
        self.assertEquals(response.context['task'], self.task2)

        # Test we can see task name, embedded youtube video and some registration info
        self.assertContains(response, 'Pokud se chceš zúčastnit celého běhu')
        self.assertContains(response, self.task2.name)
        self.assertContains(response, 'class="embed-container"')
        self.assertContains(response, 'https://www.youtube.com/embed/VUaX77nCI2g')

    def test_task3_not_registered(self):
        response = self.client.get(f'/ukol/{self.task3.uuid}')
        self.assertEquals(response.status_code, 200)
        self._assert_no_player_data_set(response)

        # We should only have task data in context
        self.assertEquals(response.context['task'], self.task3)

        # Test we can see task details, embedded youtube video and some registration info
        self.assertContains(response, 'Pokud se chceš zúčastnit celého běhu')
        self.assertContains(response, self.task3.name)
        self.assertContains(response, self.task3.text)
        self.assertContains(response, 'class="embed-container"')
        self.assertContains(response, 'https://www.youtube.com/embed/VUaX77nCI2g')

    def test_task1_registered_competitive(self):
        # Register and open Task 1
        registration_response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': 'Velký Sokol',
            'category': self.category_competitive.pk
        }, follow=True)
        response = registration_response.client.get(f'/ukol/{self.task1.uuid}')
        self.assertEquals(response.status_code, 200)

        # We should have player and task but not complete tasks data in the context
        self.assertIsNotNone(response.context['player'])
        self.assertEquals(response.context['task'], self.task1)
        self._assert_no_complete_task_data_set(response)

        # Test we can see task details
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task1.text)

        # Test that the correct time object has been created
        time = Time.objects.get(task=self.task1)
        self.assertEquals(time.player.name, 'Velký Sokol')

    def test_task2_registered_causual(self):
        # Register and open Task 2
        registration_response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': 'Sokolík',
            'category': self.category_causual.pk
        }, follow=True)
        response = registration_response.client.get(f'/ukol/{self.task2.uuid}')

        # We should have player, task and complete tasks data in the context
        self.assertIsNotNone(response.context['player'])
        self.assertEquals(response.context['task'], self.task2)
        self.assertEquals(len(response.context['complete_tasks']), 3)
        self.assertEquals(response.context['complete_tasks_total_count'], 3)
        self.assertEquals(response.context['complete_tasks_complete_count'], 1)

        # Test we can see task name and embedded youtube video
        self.assertContains(response, self.task2.name)
        self.assertContains(response, 'class="embed-container"')
        self.assertContains(response, 'https://www.youtube.com/embed/VUaX77nCI2g')

        # Test that the correct time object has been created
        time = Time.objects.get(task=self.task2)
        self.assertEquals(time.player.name, 'Sokolík')

    def test_finish_not_registered(self):
        response = self.client.get(f'/ukol/{self.task_finish.uuid}')
        self.assertEquals(response.status_code, 200)

        # We should get a warning
        self.assertContains(response, 'Nemáš vyzvednutou ani jednu kontrolu.')

        # No time object is created
        self.assertEquals(len(Time.objects.all()), 0)

    def test_finish_without_any_time(self):
        # Register and open Finish
        registration_response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': 'Sokolík',
            'category': self.category_causual.pk
        }, follow=True)
        response = registration_response.client.get(f'/ukol/{self.task_finish.uuid}')
        self.assertEquals(response.status_code, 200)

        # We should get a warning
        self.assertContains(response, 'Nemáš vyzvednutou ani jednu kontrolu.')

        # Only the time object for the registration has been created
        self.assertEquals(len(Time.objects.all()), 1)

    def test_finish_with_times(self):
        # Register, open task1 and open Finish
        registration_response = self.client.post(f'/ukol/{self.task_registration.uuid}', {
            'name': 'Sokolík',
            'category': self.category_causual.pk
        }, follow=True)
        registration_response.client.get(f'/ukol/{self.task1.uuid}')
        response = registration_response.client.get(f'/ukol/{self.task_finish.uuid}')
        self.assertEquals(response.status_code, 200)

        # We should see task name and text
        self.assertContains(response, self.task_finish.name)
        self.assertContains(response, self.task_finish.text)

        # One time object for each task should be created
        times = Time.objects.all()
        self.assertEquals(len(times), 3)
        tasks = [time.task for time in times]
        self.assertIn(self.task_registration, tasks)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task_finish, tasks)

        # player_uuid cookie is cleared
        self.assertFalse(self._get_player_uuid_from_cookie(response.client.cookies))

    def test_cookies_info(self):
        response = self.client.get('/cookies')
        self.assertEquals(response.status_code, 200)

    def _assert_correct_player_created(self, response, player_name, category):
        # player cookie is set
        self.assertIsNotNone(response.client.cookies.get('player_uuid'))

        # player is correctly created
        player_uuid = self._get_player_uuid_from_cookie(response.client.cookies)
        player = Player.objects.get(uuid=player_uuid)
        self.assertEquals(player.name, player_name)
        self.assertEquals(player.category, category)

        # registration time exists
        self.assertIsNotNone(Time.objects.get(player=player, task=self.task_registration))

    def _assert_no_player_data_set(self, response):
        self.assertIsNone(response.context['player'])
        self._assert_no_complete_task_data_set(response)

    def _assert_no_complete_task_data_set(self, response):
        self.assertFalse('complete_tasks' in response.context)
        self.assertFalse('complete_tasks_total_count' in response.context)
        self.assertFalse('complete_tasks_complete_count' in response.context)

    def _get_player_uuid_from_cookie(self, cookies):
        cookie = parse_cookie(str(cookies.get('player_uuid')))
        return cookie['Set-Cookie: player_uuid']
