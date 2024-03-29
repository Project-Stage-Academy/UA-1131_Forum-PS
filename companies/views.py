from django_filters.rest_framework import DjangoFilterBackend
from pydantic import ValidationError as PydanticValidationError
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Company
from authentication.permissions import (IsAuthenticated, IsFounder, IsInvestor,
                                        IsRelatedToCompany, IsStartup)
from forum.errors import Error as er
from notifications.decorators import create_notification_from_view
from notifications.manager import SUBSCRIPTION, UPDATE
from revision.views import CustomRevisionMixin

from .managers import LIMIT
from .managers import ArticlesManager as am
from .models import Subscription
from .permissions import EditCompanyPermission
from .serializers import CompaniesSerializer, SubscriptionSerializer


class CompaniesViewSet(CustomRevisionMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompaniesSerializer
    permission_classes = (EditCompanyPermission, IsAuthenticated)


class CompanyRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        if not pk:
            return er.NO_CREDENTIALS.response()
        try:
            company = Company.get_company(company_id=pk)
            return Response(company.get_info(), status=status.HTTP_200_OK)
        except Company.DoesNotExist:
            return er.NO_COMPANY_FOUND.response()


class CompaniesRetrieveView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        company_type = request.query_params.get('company_type')
        if not company_type:
            companies = Company.get_all_companies_info()
        else:
            companies = Company.get_all_companies_info(company_type)

        return Response(companies, status=status.HTTP_200_OK)


class SubscriptionCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    @create_notification_from_view(type=SUBSCRIPTION)
    def post(self, request, pk=None):
        if not pk:
            return er.NO_COMPANY_ID.response()
        profile_id = request.user.relation_id
        company_id = pk
        try:
            check_sub = Subscription.get_subscription(
                investor=profile_id, company=company_id)
            msg = f"You're already subscribed to {check_sub.company.brand}."
            return Response({'message': msg}, status=status.HTTP_302_FOUND)
        except Subscription.DoesNotExist:
            data = {'investor': profile_id,
                    'company': company_id}
            serializer = SubscriptionSerializer(data=data)
            if serializer.is_valid():
                res = serializer.save()
                msg = f"You're successfully subscribed to {res.company.brand}"
                return Response({'message': msg, 'subscription_id': res.subscription_id, 'company_id': company_id},
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnsubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsInvestor)

    def delete(self, request, subscription_id):
        try:
            subscription = Subscription.get_subscription(
                subscription_id=subscription_id)
        except Subscription.DoesNotExist:
            return er.SUBSCRIPTION_NOT_FOUND.response()
        company_id = subscription.company.company_id
        subscription.delete()
        return Response({'message': 'Successfully unsubscribed', 'company_id': company_id}, status=status.HTTP_200_OK)


class SubscriptionListView(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)

    def get(self, request):
        profile_id = request.user.relation_id
        subs = Subscription.get_subscriptions(investor=profile_id)
        if not subs:
            return Response({'message': "You have no subsriptions yet!"}, status=status.HTTP_200_OK)
        data = [sub.get_info() for sub in subs]
        return Response({'subscriptions': data}, status=status.HTTP_200_OK)


class RetrieveArticles(APIView):
    # do we need to block access to the articles for an unauthorized viewers?
    def get(self, request, pk=None, page=None):
        if not pk or not page:
            return Response({'error': "No company id or page was provided"}, status=status.HTTP_400_BAD_REQUEST)
        skip = LIMIT * (page - 1)
        articles = am.get_articles_for_company(pk, skip=skip, projection=['articles'])
        return Response(articles, status=status.HTTP_200_OK)


class CreateArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsStartup)

    @create_notification_from_view(type=UPDATE)
    def post(self, request):
        data = request.data
        company_id = request.user.company['company_id']
        relation_id = request.user.relation_id
        data['relation'] = relation_id
        data['company_id'] = company_id
        try:
            res = am.add_article(data)
        except PydanticValidationError as e:
            return Response({'error': er.INVALID_ARTICLE.msg}, status=er.INVALID_ARTICLE.status)
        return Response({'document_was_created': res, 'company_id': company_id}, status=status.HTTP_201_CREATED)


class UpdateArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany)

    def patch(self, request, art_id=None):
        data = request.data
        company_id = request.user.company['company_id']
        updated_article = am.update_article(company_id, art_id, data)
        return Response(updated_article)


class DeleteArticle(APIView):
    permission_classes = (IsAuthenticated, IsRelatedToCompany, IsStartup, IsFounder)

    def delete(self, request, art_id=None):
        company_id = request.user.company['company_id']
        res = am.delete_article(company_id, art_id)
        if res:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(er.Error.INVALID_ARTICLE_ID.msg, status=er.Error.INVALID_ARTICLE_ID.status)

