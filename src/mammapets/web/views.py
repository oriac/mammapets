from django.http import HttpResponse

from .forms import ContractForm, PetCareLogForm # Ensure PetCareLogForm is imported
from .models import Pet, Client, Contract, MammaPet, PetCareLog # Ensure PetCareLog is imported
from django.template import loader
from django.shortcuts import render, get_object_or_404, redirect # Ensure redirect is imported
from django.http import Http404
# from django.contrib.auth.decorators import login_required # Optional for now


def index(request):
    latest_pet_list = Pet.objects.order_by('name')[:5]
    context = {'latest_pet_list': latest_pet_list}
    return render(request, 'pets/index.html', context)


def detail(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)
    # Attempt to get an active contract
    contract = Contract.objects.filter(pet=pet, status='Active').first() 
    if not contract: # Fallback if no 'Active' contract, get the latest one if any
        contract = Contract.objects.filter(pet=pet).order_by('-end_date').first()

    mamma_pet = contract.mamma_pet if contract else None
    pet_care_logs = []
    if contract:
        # The related_name 'logs' on PetCareLog.contract ForeignKey and Meta ordering should handle sorting.
        pet_care_logs = contract.logs.all() 
    
    context = {
        'pet': pet,
        'contract': contract,
        'mamma_pet': mamma_pet,
        'pet_care_logs': pet_care_logs,
    }
    return render(request, 'pets/detail.html', context)


def contract(request):
    form = ContractForm()
    return render(request, 'pets/contract.html', {'form': form})


def new_contract(request):
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save() # commit=True by default, which is fine here
            # Assuming the 'detail' view in 'web' app is named 'detail'
            # and takes 'pet_id' as an argument.
            return redirect('web:detail', pet_id=contract.pet.id)
        else:
            # Form is invalid, re-render with errors
            return render(request, 'pets/contract.html', {'form': form})
    else: # GET request
        form = ContractForm()
        return render(request, 'pets/contract.html', {'form': form})


def user_profile(request, user_id):
    client = get_object_or_404(Client, pk=user_id)
    pets = Pet.objects.filter(owner=client)
    pets_with_care_info = []
    for pet in pets:
        contract = Contract.objects.filter(pet=pet).first()
        pets_with_care_info.append({
            'pet': pet,
            'contract': contract,
            'mamma_pet': contract.mamma_pet if contract else None,
        })
    context = {'client': client, 'pets_with_care_info': pets_with_care_info}
    return render(request, 'profiles/detail.html', context)


# @login_required # Optional for now
def add_pet_care_log(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id)
    # Basic authorization placeholder: In a real app, verify request.user is contract.mamma_pet
    # For now, we assume the user is authorized if they have the link.

    if request.method == 'POST':
        form = PetCareLogForm(request.POST, request.FILES)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.contract = contract
            # The 'date' field in PetCareLog defaults to today, so no need to set it here unless specified otherwise.
            log_entry.save()
            return redirect('web:detail', pet_id=contract.pet.id)
    else:
        form = PetCareLogForm()
    
    return render(request, 'web/add_pet_care_log.html', {
        'form': form, 
        'contract': contract,
        'pet': contract.pet # For easy access in template
    })
