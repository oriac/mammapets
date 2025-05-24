from django.test import TestCase
from django.urls import reverse
from .models import Client, Pet, MammaPet, Contract
import datetime # For creating dates for the contract

class UserProfileViewTests(TestCase):
    def setUp(self):
        self.owner = Client.objects.create(username="testowner", name="Test Owner", description="Owner desc")
        self.mamma_carer = MammaPet.objects.create(username="testcarer", name="Test Carer", phone="1234567890")

        self.pet_cared_for = Pet.objects.create(name="Buddy", description="Dog under care", owner=self.owner)
        self.pet_not_cared_for = Pet.objects.create(name="Lucy", description="Cat not under care", owner=self.owner)

        # Create a contract for Buddy
        self.contract = Contract.objects.create(
            pet=self.pet_cared_for,
            mamma_pet=self.mamma_carer,
            client=self.owner,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 12, 31),
            price=100,
            status="Active"
        )
        self.profile_url = reverse('web:user_profile', args=[self.owner.id])

    def test_user_profile_loads_correctly(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/detail.html')
        self.assertContains(response, self.owner.username)

    def test_user_profile_displays_owned_pets(self):
        response = self.client.get(self.profile_url)
        self.assertContains(response, self.pet_cared_for.name)
        self.assertContains(response, self.pet_not_cared_for.name)

    def test_user_profile_displays_pet_care_status(self):
        response = self.client.get(self.profile_url)
        # Check for pet under care
        self.assertContains(response, self.pet_cared_for.name)
        self.assertContains(response, f"Cared for by: {self.mamma_carer.username}")
        self.assertContains(response, "2024-01-01") # Check for start date
        self.assertContains(response, "2024-12-31") # Check for end date

        # Check for pet not under care
        self.assertContains(response, self.pet_not_cared_for.name)
        self.assertContains(response, "Not currently under specialized MammaPet care.")
        # Ensure the carer's name is not mistakenly associated with the pet not under care
        # This can be tricky; the simplest way is to check the overall structure in the template if this fails.
        # For now, we rely on the positive assertion for the cared-for pet and the negative message for the other.

    def test_link_on_pet_detail_page_to_owner_profile(self):
        pet_detail_url = reverse('web:detail', args=[self.pet_cared_for.id])
        response = self.client.get(pet_detail_url)
        self.assertEqual(response.status_code, 200)
        # Assert that the link to the owner's profile is present
        expected_profile_link = f'<a href="{self.profile_url}">{self.owner.username}</a>'
        self.assertContains(response, expected_profile_link, html=True)
