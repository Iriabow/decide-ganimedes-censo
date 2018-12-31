import random
from authentication.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from django.test.client import Client
from census import views
from census.views import addAllRegistered
from .models import Census
from base import mods
from voting.models import Question
from base.tests import BaseTestCase
from postproc.models import PostProcType
from voting.models import Voting

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)

        self.login(user='noadmin@gmail.com')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

        self.login(user='noadmin@gmail.com', password='qwerty')

        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_voters_registered(self):

        self.login(user='admin@gmail.com')

        q = Question(desc='test question')
        q.save()

        voting1 = Voting.objects.create(name='Voting 2', question=q, postproc_type=PostProcType.IDENTITY)
        voting1.question = q
        voting1.id = 40
        voting1.save()

        user1 = User(email='user1@user1.com')
        user1.set_password('user1user1')
        user1.city = "sevilla"
        user1.sex = "M"

        user1.save()

        user2 = User(email='user2@user2.com')
        user2.set_password('user2user2')
        user2.city = "sevilla"
        user2.sex = "W"
        user2.save()

        user3 = User(email='user3@user3.com')
        user3.set_password('user3user3')
        user3.city = "sevilla"
        user3.sex = "W"
        user3.save()

        print(Census.objects.all().values_list('voting_id', flat=True))

        data = {'voting_id': 1}
        response = self.client.get('/census/addAllRegistered/?voting_id={}/'.format(0), data, format='json')
        print(response)
        print(Voting.objects.all().values_list('id', flat=True))
        print(User.objects.all().values_list('email', flat=True))
        print(Census.objects.all().values_list('id', flat=True))
        self.assertEqual(response.status_code, 200)

    '''
    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.login(user='noadmin@gmail.com',password='qwerty')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)
        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)
    '''