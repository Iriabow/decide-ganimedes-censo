from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
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

from authentication.models import User

from census.serializer import CensusSerializer
from django.views.generic import TemplateView

from django.http import HttpResponse


class VistaBoton(TemplateView):
    template_name = 'censo.html'


def createall(request):
    voters = User.objects.all()
    voting_id = request.GET.get('voting_id')

    for voter in voters:
        try:
            census = Census(voting_id=voting_id, voter_id=voter.id)
            census.save()

        except IntegrityError:
            continue

    html = "<html><body> It is now %s.</body></html>"
    return HttpResponse(html)


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (CensusPermissions,)
    serializer_class = CensusSerializer

    def create(self, request, *args, **kwargs):

        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')

        users = User.objects.all().values_list('id')

        print(type(users))
        try:
            for voter in voters:
                if voter not in users:
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
