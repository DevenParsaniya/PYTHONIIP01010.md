from django.shortcuts import render

# Create your views here.

# ViewSets
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly, IsInvitedToPrivateEvent]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['title', 'location', 'organizer']
    search_fields = ['title', 'description']

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='rsvp')
    def create_rsvp(self, request, pk=None):
        event = Event.objects.get(pk=pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        event = Event.objects.get(pk=self.kwargs['event_id'])
        serializer.save(event=event, user=self.request.user)
