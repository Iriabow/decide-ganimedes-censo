from django.contrib import messages
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import CensusPermissions
from .models import Census
from voting.models import Voting
from authentication.models import User
from census.serializer import CensusSerializer


def addAllRegistered(request):

    voters = User.objects.all()
    voting_id = request.GET.get('voting_id')
    list_voting = list(Voting.objects.all().values_list('id', flat=True))
    if request.user.is_staff:
        if int(voting_id) in list_voting:
            for voter in voters:
                try:
                    census = Census(voting_id=voting_id, voter_id=voter.id)
                    census.save()
                except IntegrityError:
                    continue
        else:
            messages.add_message(request, messages.ERROR, "Invalid voting id: " + str(voting_id))
    else:
        messages.add_message(request, messages.ERROR, "Permission denied")

    return redirect('/admin/census/census')


def addAllBySex(request):

    voting_id = request.GET.get('voting_id')
    sex = request.GET.get('sex')
    voters = User.objects.filter(sex=sex)

    list_voting = set(Voting.objects.all().values_list('id', flat=True))

    if request.user.is_staff:
        if voters:
            if int(voting_id) in list_voting:
                for voter in voters:
                    try:
                        census = Census(voting_id=voting_id, voter_id=voter.id)
                        census.save()
                    except IntegrityError:
                        continue
            else:
                messages.add_message(request, messages.ERROR, "Invalid voting id")
        else:
                messages.add_message(request, messages.WARNING, "No users with sex requested")
    else:
        messages.add_message(request, messages.ERROR, "Permission denied")

    #return redirect('/census/?voting_id=' + voting_id)
    return redirect('/admin/census/census')


def addAllInCity(request):

    voting_id = request.GET.get('voting_id')
    city = request.GET.get('city')
    voters = User.objects.filter(city__iexact=city)

    list_voting = set(Voting.objects.all().values_list('id', flat=True))

    if request.user.is_staff:
        if voters:
            if int(voting_id) in list_voting:
                for voter in voters:
                    try:
                        census = Census(voting_id=voting_id, voter_id=voter.id)
                        census.save()
                    except IntegrityError:
                        continue
            else:
                messages.add_message(request, messages.ERROR, "Invalid voting id")
        else:
                messages.add_message(request, messages.WARNING, "No users in city requested")
    else:
        messages.add_message(request, messages.ERROR, "Permission denied")

    #return redirect('/census/?voting_id=' + voting_id)
    return redirect('/admin/census/census')


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (CensusPermissions,)
    serializer_class = CensusSerializer

    def create(self, request, *args, **kwargs):

        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')

        users = User.objects.all().values_list('id', flat=True)

        print(type(users))
        try:
            for voter in voters:
                if int(voter) not in users:
                    return Response('Voter id does not exist', status=ST_409)

                else:
                    census = Census(voting_id=voting_id, voter_id=voter)
                    census.save()

        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')
