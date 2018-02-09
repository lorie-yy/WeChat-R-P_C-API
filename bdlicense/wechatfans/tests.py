from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from models import shop_discountinfo
from serializers import Shop_discountinfoSerializer


@api_view(['GET', 'POST'])
def snippet_list(request):

    if request.method == 'POST':
        snippets = shop_discountinfo.objects.all()
        serializer = Shop_discountinfoSerializer(snippets, many=True)
        print "333333333333"
        return Response(serializer.data, status=status.HTTP_201_CREATED)
