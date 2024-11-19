from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Article, LigneReservation, Reservation, Activite
from .serializers import ArticleSerializer, LigneReservationSerializer, ReservationSerializer, ActiviteSerializer


# Vue pour la liste et la création de réservations
class LigneReservationListCreateView(APIView):
    permission_classes = [IsAuthenticated]  # S'assurer que l'utilisateur est authentifié

    def get(self, request):
        # Vérification du paramètre 'reservation_id'
        reservation_id = request.query_params.get('reservation_id', None)
        
        if reservation_id:
            # Si 'reservation_id' est passé, récupérer la réservation spécifique
            try:
                reservation = Reservation.objects.get(id=reservation_id)
                ligne_reservations = LigneReservation.objects.filter(reservation=reservation)
                serializer = LigneReservationSerializer(ligne_reservations, many=True)
                return Response(serializer.data)
            except Reservation.DoesNotExist:
                return Response({"error": "Réservation non trouvée."}, status=404)

        # Filtrer les réservations pour l'utilisateur connecté
        # Ici, nous devons nous assurer que l'utilisateur est lié à la réservation d'une manière ou d'une autre.
        # Par exemple, si l'utilisateur est lié via 'LigneReservation', vous devez adapter la logique en fonction du modèle.
        ligne_reservations = LigneReservation.objects.filter(reservation__activite__planning__metier__formateurs__utilisateur=request.user)

        serializer = LigneReservationSerializer(ligne_reservations, many=True)
        return Response(serializer.data)
    

# Vue pour récupérer la liste des articles
class ArticleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        articles = Article.objects.all().select_related('categorie')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


# Vue pour récupérer les détails d'une activité
class ActiviteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Récupérer les détails d'une activité spécifique."""
        try:
            activite = Activite.objects.get(pk=pk)
            serializer = ActiviteSerializer(activite)
            return Response(serializer.data)
        except Activite.DoesNotExist:
            return Response({'error': 'Activité non trouvée'}, status=404)


# Vue pour récupérer une réservation spécifique et ses détails
class ReservationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Récupérer les détails d'une réservation spécifique."""
        reservation = get_object_or_404(Reservation, pk=pk, activite__created_by=request.user)
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

class LigneReservationListView(generics.ListCreateAPIView):
    queryset = LigneReservation.objects.all()
    serializer_class = LigneReservationSerializer