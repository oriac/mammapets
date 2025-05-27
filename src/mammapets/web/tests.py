from django.test import TestCase
from django.urls import reverse
from .models import Client, Pet, MammaPet, Contract, PetCareLog # Added PetCareLog
import datetime # For creating dates for the contract
from django.utils import timezone # Added timezone
from django.core.files.uploadedfile import SimpleUploadedFile # Added SimpleUploadedFile
import os # Added os
from django.conf import settings # Added settings


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


class PetCareLogViewTests(TestCase):
    def setUp(self):
        self.owner = Client.objects.create(username="logowner", name="Log Owner")
        self.carer = MammaPet.objects.create(username="logcarer", name="Log Carer", phone="0987654321")
        self.pet = Pet.objects.create(name="TimelinePet", description="Pet with timeline", owner=self.owner)
        
        self.contract = Contract.objects.create(
            pet=self.pet,
            mamma_pet=self.carer,
            client=self.owner,
            start_date=timezone.now().date() - datetime.timedelta(days=5),
            end_date=timezone.now().date() + datetime.timedelta(days=25),
            price=200,
            status="Active" # Important for consistent testing with view logic
        )

        # Create a dummy image file for uploads
        self.dummy_image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        self.dummy_image = SimpleUploadedFile("test_photo.gif", self.dummy_image_content, content_type="image/gif")
        
        # Pre-create one log entry for testing display
        self.log_with_photo_and_notes = PetCareLog.objects.create(
            contract=self.contract,
            notes="Test log with photo and notes.",
            photo=self.dummy_image
        )
        # Reset file pointer for potential re-use if needed, though new SimpleUploadedFile is better
        self.dummy_image.seek(0) 

        self.log_with_notes_only = PetCareLog.objects.create(
            contract=self.contract,
            notes="Test log with notes only."
        )

        self.add_log_url = reverse('web:add_pet_care_log', args=[self.contract.id])
        self.pet_detail_url = reverse('web:detail', args=[self.pet.id])

    # def tearDown(self):
    #     # This is complex because file paths are dynamic with dates.
    #     # A more robust solution might involve mocking storage or using a temporary MEDIA_ROOT.
    #     # For now, we'll skip aggressive auto-cleanup in tearDown for simplicity,
    #     # but be aware that test files might accumulate in MEDIA_ROOT.
    #     pass

    def test_pet_care_log_model_str(self):
        self.assertEqual(str(self.log_with_photo_and_notes), f"Log for {self.pet.name} on {self.log_with_photo_and_notes.date}")

    def test_add_pet_care_log_view_get(self):
        # Basic test without login for now
        response = self.client.get(self.add_log_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/add_pet_care_log.html')
        # Need to import PetCareLogForm from .forms for this check
        from .forms import PetCareLogForm 
        self.assertIsInstance(response.context['form'], PetCareLogForm)
        self.assertEqual(response.context['contract'], self.contract)

    def test_add_pet_care_log_view_post_success(self):
        # Reset file pointer before each use in POST
        another_dummy_image = SimpleUploadedFile("another_test.gif", self.dummy_image_content, content_type="image/gif")
        log_count_before = PetCareLog.objects.count()
        post_data = {
            'notes': 'Posted notes.',
            'photo': another_dummy_image 
        }
        response = self.client.post(self.add_log_url, data=post_data)
        
        self.assertEqual(response.status_code, 302) # Redirects on success
        self.assertRedirects(response, self.pet_detail_url)
        self.assertEqual(PetCareLog.objects.count(), log_count_before + 1)
        new_log = PetCareLog.objects.latest('timestamp')
        self.assertEqual(new_log.contract, self.contract)
        self.assertEqual(new_log.notes, 'Posted notes.')
        self.assertTrue(new_log.photo.name.endswith('another_test.gif'))
        # Optionally clean up the created file if MEDIA_ROOT is accessible and path is known
        if new_log.photo and hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            photo_path = os.path.join(settings.MEDIA_ROOT, new_log.photo.name)
            if os.path.exists(photo_path):
                os.remove(photo_path)


    def test_add_pet_care_log_view_post_invalid(self):
        log_count_before = PetCareLog.objects.count()
        # Post data without the required 'photo' field (if photo is required by form/model)
        # PetCareLogForm makes photo required by default as it's an ImageField.
        # Actually, in forms.py, PetCareLogForm fields are ['notes', 'photo'], and ImageField is not required by default.
        # To make this test meaningful for invalidity, let's assume notes are required or submit empty data.
        # However, the current PetCareLogForm does not make 'notes' explicitly required.
        # Let's test by submitting data that would make the form invalid if 'notes' were required,
        # or by ensuring photo is truly required.
        # Based on current PetCareLog model: notes can be blank, photo is an ImageField (which is not required by default at form level unless explicitly set)
        # The form PetCareLogForm has fields = ['notes', 'photo']. ImageField in a model is not required by default.
        # To make this test fail, let's assume 'notes' was required or we submit something that makes a field invalid.
        # For now, let's assume an empty post would be invalid if a field was required.
        # The current form doesn't have any fields that are *always* required by default *and* tested here.
        # Let's change this to check for invalid form by submitting nothing, which should fail if any field was required.
        # However, both notes (blank=True) and photo (ImageField) are not strictly required by the model/form as is.
        # To properly test invalid, we'd need a field that IS required, or mock the form to be invalid.
        # For now, this test as written in prompt might pass if both fields can be empty/missing.
        # The prompt implies photo is required. ImageField(blank=False) would make it so.
        # Let's assume photo is required for this test to be meaningful as an "invalid" test.
        # If PetCareLog.photo cannot be null/blank, then this test is valid.
        # PetCareLog.photo is models.ImageField(upload_to='pet_care_logs/%Y/%m/%d/')
        # This does not set null=True or blank=True, so it IS required at the model level.
        # Thus, submitting without it should make the form invalid.
        post_data = {'notes': 'Trying to post without photo.'}
        response = self.client.post(self.add_log_url, data=post_data)
        
        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors) # Check for form errors
        self.assertEqual(PetCareLog.objects.count(), log_count_before) # No new log created

    def test_pet_detail_view_displays_timeline_and_link(self):
        response = self.client.get(self.pet_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pets/detail.html')

        self.assertContains(response, "Pet Care Timeline")
        # Check for log with photo and notes
        self.assertContains(response, self.log_with_photo_and_notes.notes)
        # Ensure the photo URL is part of the response content
        self.assertContains(response, self.log_with_photo_and_notes.photo.url)
        
        # Check for log with notes only
        self.assertContains(response, self.log_with_notes_only.notes)
        
        # Check for "Add Log" link
        self.assertContains(response, f'href="{self.add_log_url}"')

    def test_pet_detail_view_no_logs_message(self):
        # Create a new contract and pet without any logs
        new_pet = Pet.objects.create(name="NoLogPet", owner=self.owner)
        new_contract = Contract.objects.create(
            pet=new_pet, mamma_pet=self.carer, client=self.owner, 
            start_date=timezone.now().date(), end_date=timezone.now().date() + datetime.timedelta(days=10),
            status="Active"
        )
        no_log_pet_detail_url = reverse('web:detail', args=[new_pet.id])
        response = self.client.get(no_log_pet_detail_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No care logs have been added for this contract period yet.")
        self.assertNotContains(response, self.log_with_photo_and_notes.notes) # Ensure other logs are not showing up


# New tests for ContractForm, PetCareLogForm, Contract model, and new_contract view

from django.forms import DateInput
from .forms import ContractForm, PetCareLogForm
from django.core.exceptions import ValidationError

class ContractFormTests(TestCase):
    def test_contract_form_date_widgets_and_attrs(self):
        form = ContractForm()
        # Check start_date
        self.assertIsInstance(form.fields['start_date'].widget, DateInput)
        self.assertEqual(form.fields['start_date'].widget.attrs['class'], 'datepicker')
        self.assertEqual(form.fields['start_date'].widget.attrs['placeholder'], 'MM/DD/YYYY')
        # Check end_date
        self.assertIsInstance(form.fields['end_date'].widget, DateInput)
        self.assertEqual(form.fields['end_date'].widget.attrs['class'], 'datepicker')
        self.assertEqual(form.fields['end_date'].widget.attrs['placeholder'], 'MM/DD/YYYY')

    def test_valid_contract_form_data(self):
        # Create necessary related objects
        owner = Client.objects.create(username="formowner", name="Form Owner")
        pet = Pet.objects.create(name="FormPet", owner=owner)
        mamma_pet = MammaPet.objects.create(username="formcarer", name="Form Carer")
        
        form_data = {
            'start_date': '01/01/2025',
            'end_date': '01/31/2025',
            'pet': pet.id,
            'mamma_pet': mamma_pet.id,
            'client': owner.id,
            'price': 100.00
        }
        form = ContractForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_invalid_contract_form_missing_fields(self):
        form_data = {'price': 100.00} # Missing required fields
        form = ContractForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)
        self.assertIn('pet', form.errors)
        self.assertIn('mamma_pet', form.errors)
        self.assertIn('client', form.errors)


class PetCareLogFormTests(TestCase):
    def test_no_end_date_field_in_pet_care_log_form(self):
        form = PetCareLogForm()
        self.assertNotIn('end_date', form.fields)

    def test_valid_pet_care_log_form(self):
        # Create a dummy image file for uploads
        dummy_image_content = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        dummy_image = SimpleUploadedFile("test_log_photo.gif", dummy_image_content, content_type="image/gif")
        
        form_data = {'notes': 'This is a test log entry.'}
        file_data = {'photo': dummy_image}
        form = PetCareLogForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid(), form.errors.as_text())


class ContractModelTests(TestCase):
    def setUp(self):
        self.owner = Client.objects.create(username="modelowner", name="Model Owner")
        self.pet = Pet.objects.create(name="ModelPet", owner=self.owner)
        self.mamma_carer = MammaPet.objects.create(username="modelcarer", name="Model Carer")

    def test_contract_status_default(self):
        contract = Contract.objects.create(
            pet=self.pet,
            mamma_pet=self.mamma_carer,
            client=self.owner,
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=30),
            price=150
        )
        self.assertEqual(contract.status, Contract.ContractStatus.PENDING)

    def test_contract_status_valid_choice(self):
        contract = Contract(
            pet=self.pet,
            mamma_pet=self.mamma_carer,
            client=self.owner,
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=30),
            price=150,
            status=Contract.ContractStatus.ACTIVE
        )
        contract.full_clean() # Should not raise ValidationError
        contract.save()
        self.assertEqual(contract.status, Contract.ContractStatus.ACTIVE)

    def test_contract_status_invalid_choice(self):
        with self.assertRaises(ValidationError):
            contract = Contract(
                pet=self.pet,
                mamma_pet=self.mamma_carer,
                client=self.owner,
                start_date=timezone.now(),
                end_date=timezone.now() + datetime.timedelta(days=30),
                price=150,
                status="INVALID_STATUS" # An invalid choice
            )
            contract.full_clean() # This should raise ValidationError


class NewContractViewTests(TestCase):
    def setUp(self):
        self.owner = Client.objects.create(username="viewowner", name="View Owner")
        self.pet = Pet.objects.create(name="ViewPet", owner=self.owner)
        self.mamma_carer = MammaPet.objects.create(username="viewcarer", name="View Carer")
        self.new_contract_url = reverse('web:new_contract')
        self.pet_detail_url = reverse('web:detail', args=[self.pet.id])

    def test_new_contract_view_get(self):
        response = self.client.get(self.new_contract_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pets/contract.html')
        self.assertIsInstance(response.context['form'], ContractForm)

    def test_new_contract_view_post_valid(self):
        form_data = {
            'start_date': '01/01/2026',
            'end_date': '01/31/2026',
            'pet': self.pet.id,
            'mamma_pet': self.mamma_carer.id,
            'client': self.owner.id,
            'price': 200.00
        }
        contract_count_before = Contract.objects.count()
        response = self.client.post(self.new_contract_url, data=form_data)
        
        self.assertEqual(Contract.objects.count(), contract_count_before + 1)
        # The redirect URL depends on the created contract's pet ID.
        # Since we use self.pet, its ID is fixed for this test.
        created_contract = Contract.objects.latest('id') # Assuming id is auto-incrementing PK
        self.assertRedirects(response, reverse('web:detail', args=[created_contract.pet.id]))


    def test_new_contract_view_post_invalid(self):
        form_data = {'price': 200.00} # Missing required fields
        contract_count_before = Contract.objects.count()
        response = self.client.post(self.new_contract_url, data=form_data)

        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertTemplateUsed(response, 'pets/contract.html')
        self.assertIsInstance(response.context['form'], ContractForm)
        self.assertTrue(response.context['form'].errors) # Check for form errors
        self.assertEqual(Contract.objects.count(), contract_count_before) # No new contract created
