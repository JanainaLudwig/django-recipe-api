from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from utils.test import create_user

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """test the public available ingredients API"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """test that login is required to access ingredients endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """test the private ingredients API"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_user_can_retrieve_ingredients_list(self):
        """test user can retrive ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that only authenticated user ingredients are returned"""
        user2 = create_user(email='test2@test.com')
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingredient = Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
