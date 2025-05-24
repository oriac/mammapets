from django.http import HttpResponse

from .forms import ContractForm
from .models import Pet, Client, Contract
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.http import Http404


def index(request):
    latest_pet_list = Pet.objects.order_by('name')[:5]
    context = {'latest_pet_list': latest_pet_list}
    return render(request, 'pets/index.html', context)


def detail(request, pet_id):
    pet = get_object_or_404(Pet, pk=pet_id)
    contract = Contract.objects.filter(pet=pet).first()
    mamma_pet = contract.mamma_pet if contract else None
    return render(request, 'pets/detail.html', {'pet': pet, 'contract': contract, 'mamma_pet': mamma_pet})


def results(request, pet_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % pet_id)


def vote(request, pet_id):
    return HttpResponse("You're voting on question %s." % pet_id)


def contract(request):
    form = ContractForm()
    return render(request, 'pets/contract.html', {'form': form})


def new_contract(request):
    form = ContractForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return HttpResponse("contract saved")
    return HttpResponse("contract not saved")


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
