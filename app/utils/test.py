from django.contrib.auth import get_user_model


def create_user(email='test@test.com', password='testpass', name='test name'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        name=name
    )
