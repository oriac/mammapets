from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime, timezone
from .models import Person, Client, Pet, MammaPet, Contract
from .forms import ContractForm


class ModelTests(TestCase):
    """Tests for the core models"""
    
    def setUp(self):
        """Set up test data"""
        self.client_obj = Client.objects.create(
            username='testclient',
            name='Test Client',
            description='A test client',
            address='123 Test St'
        )
        
        self.pet = Pet.objects.create(
            name='Fluffy',
            description='A fluffy cat',
            owner=self.client_obj
        )
        
        self.mamma_pet = MammaPet.objects.create(
            username='testmamma',
            name='Test Mamma',
            description='A test mamma pet sitter',
            phone='555-1234'
        )
    
    def test_person_str(self):
        """Test Person model string representation"""
        person = Person.objects.create(
            username='testuser',
            name='Test User',
            description='Test description'
        )
        self.assertEqual(str(person), 'testuser')
    
    def test_client_str(self):
        """Test Client model string representation"""
        self.assertEqual(str(self.client_obj), 'testclient')
    
    def test_client_inheritance(self):
        """Test Client inherits from Person"""
        self.assertIsInstance(self.client_obj, Person)
        self.assertEqual(self.client_obj.address, '123 Test St')
    
    def test_pet_str(self):
        """Test Pet model string representation"""
        self.assertEqual(str(self.pet), 'Fluffy')
    
    def test_pet_owner_relationship(self):
        """Test Pet-Client relationship"""
        self.assertEqual(self.pet.owner, self.client_obj)
    
    def test_mamma_pet_str(self):
        """Test MammaPet model string representation"""
        self.assertEqual(str(self.mamma_pet), 'testmamma')
    
    def test_mamma_pet_inheritance(self):
        """Test MammaPet inherits from Person"""
        self.assertIsInstance(self.mamma_pet, Person)
        self.assertEqual(self.mamma_pet.phone, '555-1234')
    
    def test_contract_creation(self):
        """Test Contract model creation and relationships"""
        contract = Contract.objects.create(
            start_date=datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc),
            end_date=datetime(2023, 1, 7, 18, 0, tzinfo=timezone.utc),
            pet=self.pet,
            mamma_pet=self.mamma_pet,
            client=self.client_obj,
            price=100.0,
            status='active'
        )
        
        self.assertEqual(str(contract), 'active')
        self.assertEqual(contract.pet, self.pet)
        self.assertEqual(contract.mamma_pet, self.mamma_pet)
        self.assertEqual(contract.client, self.client_obj)
        self.assertEqual(contract.price, 100.0)


class ViewTests(TestCase):
    """Tests for the core views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = TestClient()
        
        self.client_obj = Client.objects.create(
            username='testclient',
            name='Test Client',
            description='A test client',
            address='123 Test St'
        )
        
        self.pet1 = Pet.objects.create(
            name='Alpha',
            description='First pet',
            owner=self.client_obj
        )
        
        self.pet2 = Pet.objects.create(
            name='Beta',
            description='Second pet',
            owner=self.client_obj
        )
        
        self.mamma_pet = MammaPet.objects.create(
            username='testmamma',
            name='Test Mamma',
            description='A test mamma pet sitter',
            phone='555-1234'
        )
    
    def test_index_view(self):
        """Test index view displays pets ordered by name"""
        response = self.client.get(reverse('web:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha')
        self.assertContains(response, 'Beta')
        self.assertIn('latest_pet_list', response.context)
        
        # Test pets are ordered by name
        pets = list(response.context['latest_pet_list'])
        self.assertEqual(pets[0].name, 'Alpha')
        self.assertEqual(pets[1].name, 'Beta')
    
    def test_index_view_no_pets(self):
        """Test index view when no pets exist"""
        Pet.objects.all().delete()
        response = self.client.get(reverse('web:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No pets are available')
    
    def test_detail_view(self):
        """Test detail view displays pet information"""
        response = self.client.get(reverse('web:detail', args=[self.pet1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha')
        self.assertIn('pet', response.context)
        self.assertEqual(response.context['pet'], self.pet1)
    
    def test_detail_view_nonexistent_pet(self):
        """Test detail view returns 404 for non-existent pet"""
        response = self.client.get(reverse('web:detail', args=[9999]))
        self.assertEqual(response.status_code, 404)
    
    def test_results_view(self):
        """Test results view returns correct response"""
        response = self.client.get(reverse('web:results', args=[self.pet1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"You're looking at the results of question {self.pet1.id}")
    
    def test_vote_view(self):
        """Test vote view returns correct response"""
        response = self.client.get(reverse('web:vote', args=[self.pet1.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"You're voting on question {self.pet1.id}")
    
    def test_contract_view(self):
        """Test contract view displays form"""
        response = self.client.get(reverse('web:contract'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ContractForm)
    
    def test_new_contract_valid_data(self):
        """Test new_contract view with valid data"""
        data = {
            'start_date': '2023-01-01 10:00:00',
            'end_date': '2023-01-07 18:00:00',
            'pet': self.pet1.id,
            'mamma_pet': self.mamma_pet.id,
            'client': self.client_obj.id,
            'price': 150.0,
        }
        
        response = self.client.post(reverse('web:new_contract'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contract saved')
        
        # Verify contract was created
        contract = Contract.objects.get(pet=self.pet1)
        self.assertEqual(contract.price, 150.0)
        self.assertEqual(contract.pet, self.pet1)
    
    def test_new_contract_invalid_data(self):
        """Test new_contract view with invalid data"""
        data = {
            # Missing required fields
            'start_date': '2023-01-01 10:00:00',
        }
        
        response = self.client.post(reverse('web:new_contract'), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contract not saved')
        
        # Verify no contract was created
        self.assertEqual(Contract.objects.count(), 0)


class FormTests(TestCase):
    """Tests for the forms"""
    
    def setUp(self):
        """Set up test data"""
        self.client_obj = Client.objects.create(
            username='testclient',
            name='Test Client',
            description='A test client',
            address='123 Test St'
        )
        
        self.pet = Pet.objects.create(
            name='Fluffy',
            description='A fluffy cat',
            owner=self.client_obj
        )
        
        self.mamma_pet = MammaPet.objects.create(
            username='testmamma',
            name='Test Mamma',
            description='A test mamma pet sitter',
            phone='555-1234'
        )
    
    def test_contract_form_valid_data(self):
        """Test ContractForm with valid data"""
        form_data = {
            'start_date': '2023-01-01 10:00:00',
            'end_date': '2023-01-07 18:00:00',
            'pet': self.pet.id,
            'mamma_pet': self.mamma_pet.id,
            'client': self.client_obj.id,
            'price': 200.0,
        }
        
        form = ContractForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test form save
        contract = form.save()
        self.assertEqual(contract.price, 200.0)
        self.assertEqual(contract.pet, self.pet)
    
    def test_contract_form_missing_required_fields(self):
        """Test ContractForm with missing required fields"""
        form_data = {
            'start_date': '2023-01-01 10:00:00',
            # Missing other required fields
        }
        
        form = ContractForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check that required fields are in errors
        self.assertIn('end_date', form.errors)
        self.assertIn('pet', form.errors)
        self.assertIn('mamma_pet', form.errors)
        self.assertIn('client', form.errors)
    
    def test_contract_form_empty_data(self):
        """Test ContractForm with no data"""
        form = ContractForm(data={})
        self.assertFalse(form.is_valid())
        
        # All required fields should have errors
        required_fields = ['start_date', 'end_date', 'pet', 'mamma_pet', 'client']
        for field in required_fields:
            self.assertIn(field, form.errors)


class URLTests(TestCase):
    """Tests for URL routing"""
    
    def test_index_url(self):
        """Test index URL resolves correctly"""
        url = reverse('web:index')
        self.assertEqual(url, '/web/')
    
    def test_detail_url(self):
        """Test detail URL resolves correctly"""
        url = reverse('web:detail', args=[1])
        self.assertEqual(url, '/web/1/')
    
    def test_results_url(self):
        """Test results URL resolves correctly"""
        url = reverse('web:results', args=[1])
        self.assertEqual(url, '/web/1/results/')
    
    def test_vote_url(self):
        """Test vote URL resolves correctly"""
        url = reverse('web:vote', args=[1])
        self.assertEqual(url, '/web/1/vote/')
    
    def test_contract_url(self):
        """Test contract URL resolves correctly"""
        url = reverse('web:contract')
        self.assertEqual(url, '/web/contract/')
    
    def test_new_contract_url(self):
        """Test new_contract URL resolves correctly"""
        url = reverse('web:new_contract')
        self.assertEqual(url, '/web/new_contract/')
