from typing import Dict

import pymongo
from django.core.mail import EmailMessage
from pydantic import BaseModel, ValidationError
from pymongo.errors import PyMongoError
from rest_framework_simplejwt.exceptions import (AuthenticationFailed,
                                                 TokenError)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authentication.models import CustomUser

from .errors import Error
from .settings import EMAIL_HOST, EMAIL_HOST_USER


class TokenManager:

    @classmethod
    def generate_access_token_for_user(cls, user: CustomUser) -> AccessToken:
        """Generates token for user"""

        access_token = AccessToken.for_user(user)
        return access_token

    @classmethod
    def generate_refresh_token_for_user(cls, user: CustomUser) -> RefreshToken:
        """Generates token for user"""

        refresh_token = RefreshToken.for_user(user)
        return refresh_token

    @classmethod
    def generate_token_with_payload(cls, payload, token=None):
        decoded_token = cls.__get_decoded_access_token(token)
        decoded_token.payload = {**decoded_token.payload, **payload}
        return str(decoded_token)

    @classmethod
    def generate_company_related_token(cls, company_id: int, token=None):
        return cls.generate_token_with_payload({'company_id': company_id}, token)

    @classmethod
    def get_access_payload(cls, token: str) -> dict:
        """Returns payload for access token as dict"""

        decoded_token = cls.__get_decoded_access_token(token)
        return decoded_token.payload

    @classmethod
    def get_refresh_payload(cls, token: str) -> tuple:
        """Returns payload for refresh token as tuple with refresh and access tokens"""

        decoded_tokens = cls.__get_decoded_refresh_token(token)
        return decoded_tokens

    @classmethod
    def __get_decoded_access_token(cls, token) -> AccessToken:
        """Returns decoded token as Dict"""

        try:
            decoded_token = AccessToken(token)
        except TokenError:
            raise AuthenticationFailed(detail=Error.INVALID_TOKEN.msg)
        return decoded_token

    @classmethod
    def __get_decoded_refresh_token(cls, token) -> tuple[RefreshToken, AccessToken]:
        """Returns tuple with decoded tokens as Dict"""

        try:
            decoded_token = RefreshToken(token)
            decoded_access_token = decoded_token.access_token
        except TokenError:
            raise AuthenticationFailed(detail=Error.INVALID_TOKEN.msg)
        return decoded_token, decoded_access_token


class MongoManager:
    db = None
    types = {}

    @classmethod
    def id_to_string(cls, document):
        """Changes _id field of returned document from ObjectId to string."""
        try:
            document['_id'] = str(document['_id'])
        except (KeyError, TypeError):
            pass
        return document

    @classmethod
    def to_list(cls, cursor):
        """Returns the list of objects from the PyMongo cursor."""

        res = []
        for el in cursor:
            res.append(cls.id_to_string(el))
        return res

    @classmethod
    def check_if_exist(cls, query):
        """Checks if the document that matching to the given filter exist."""
        res = cls.db.count_documents(query)
        if not res:
            return False
        return True

    @classmethod
    def get_document(cls, query, **kwargs):
        """Retrieves the document from the database."""
        document = cls.db.find_one(query, **kwargs)
        return cls.id_to_string(document)

    @classmethod
    def get_documents(cls, query, **kwargs):
        """Retrieves the multiple documents from the database."""
        document = cls.db.find(query, **kwargs)
        return cls.to_list(document)

    @classmethod
    def get_and_sort_documents(cls, query, sort_options=None, **kwargs):
        """Retrieves the multiple documents from the database and sorts it.
           Args for sorting: pass as a list with this args:
               - key_or_list: a single key or a list of (key, direction)
                 pairs specifying the keys to sort on
               - direction (optional): only used if key_or_list is a single key,
                 if not given ASCENDING is assumed
        """
        if sort_options is None:
            sort_options = []
        documents = cls.db.find(query, **kwargs).sort(*sort_options)
        return cls.to_list(documents)

    @classmethod
    def create_document(cls, data, key) -> str | None:
        """Creates document. Key is needed to use proper model for validation."""
        model: BaseModel = cls.types[key]
        validated_model = model.model_validate(data)
        res = cls.db.insert_one(validated_model.model_dump())
        return str(res.inserted_id) if res.acknowledged else None

    @classmethod
    def update_document(cls, query, update, **kwargs):
        """Updates the document."""
        document = cls.db.find_one_and_update(query, update, return_document=pymongo.ReturnDocument.AFTER, **kwargs)
        return cls.id_to_string(document)

    @classmethod
    def delete_document(cls, query, **kwargs):
        """Delete the document from database."""
        res = cls.db.find_one_and_delete(query, **kwargs)
        return cls.id_to_string(res)

    @classmethod
    def delete_from_document(cls, query, delete_part, **kwargs):
        """Deletes the specific part of the document."""
        res = cls.db.update_one(query, delete_part, **kwargs)
        if res.modified_count == 0:
            return None
        return res

    @classmethod
    def delete_documents(cls, query, **kwargs):
        try:
            res = cls.db.delete_many(query, **kwargs)
            return res.deleted_count
        except PyMongoError:
            return None


class EmailManager:
    @staticmethod
    def _email_sender(data: Dict):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()

    @staticmethod
    def _data_formatter(email_subject: str, email_body: str, email: str):
        return {
            'email_subject': email_subject,
            'email_body': email_body,
            'from_email': EMAIL_HOST_USER,
            'to_email': email
        }
