from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import RFQ
from .services import compare_quotes


class QuoteComparisonView(APIView):

    def get(self, request, rfq_id):

        try:
            rfq = RFQ.objects.get(id=rfq_id)
        except RFQ.DoesNotExist:
            return Response(
                {
                    'detail': 'RFQ not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        comparison = compare_quotes(rfq)

        return Response({
            'rfq': rfq.rfq_number,
            'results': comparison
        })