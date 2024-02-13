from django.shortcuts import render
from .models import *
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import datetime
import logging

app_name = 'api'

# Create your views here.

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmation = request.POST.get('confirm-password')
        if password != confirmation:
            return JsonResponse({'message': "Passwords must match."})
            

        try:
            user = CustomUser.objects.create_user(username,email, password)
            user.save()
            return JsonResponse({'message': 'User created successfully'})
        except IntegrityError:
            return JsonResponse({'message': 'Username already taken'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_authenticated:
                session_id = request.session.session_key
                print("Session Id: ", session_id)
                return JsonResponse({'message': 'Logged in', 'success': True,'session_id': session_id, 'user_id': user.id})
            else:
                return JsonResponse({'message': 'User is not authenticated', 'success': False})
        else:
            return JsonResponse({'message': 'Invalid username and/or password.', 'success': False})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

@csrf_exempt
def logout_view(request):
    logout(request)

    if not request.user.is_authenticated:
        session_id = request.session.session_key
        return JsonResponse({'message': 'Logged out', 'success': True,'session_id': session_id})
    

def get_user_from_session(request,head=False):
    try:

        

        if head==True:
            session_id = request.META.get('HTTP_AUTHORIZATION', '')
            print(session_id)
        else:
            session_id = request.body.decode()

        session = Session.objects.get(session_key=session_id)
        user_id = session.get_decoded().get('_auth_user_id')
        user = CustomUser.objects.get(pk=user_id)

        return user
    except:
        return None
    
@csrf_exempt
def is_authenticated(request):
    
        user = get_user_from_session(request)
    
        if not user == None:
    
            is_authenticated = user.is_authenticated
            return JsonResponse({'is_authenticated': is_authenticated,'email':user.email})
        else:
            return JsonResponse({'is_authenticated': False})


#gets detail of the products
def product_detail_getter(products):
   
    product_data = []

    for product in products:
        product_info = {
            'id':product.id,
            'name':product.name,
            'description': product.description,
            'image': product.image.url,
            'store': []
        }

        prices = ProductPrice.objects.filter(product=product)

        for price in prices:
            store_info = {
                'store_name': price.store.name,
                'store_location': price.store.link,
                'price': str(price.price),  # Convert Decimal to string for JSON serialization
            }
            product_info['store'].append(store_info)

        product_data.append(product_info)

    return product_data
    
def all_products(request):
    products = Product.objects.all()
    product_data = product_detail_getter(products)
    
    return JsonResponse({'products': product_data})



@csrf_exempt
def search(request):
    if request.method == "POST":
        user = get_user_from_session(request,True)

        # Validate and sanitize input
        query = request.POST.get('query')
        if not query:
            return JsonResponse({'error': 'Invalid query'}, status=400)

        products = Product.objects.filter(name__icontains=query)
        product_data = product_detail_getter(products)

        if user and user.is_authenticated:
            # Use try/except for model creation
            try:
                search_entries = [
                    SearchEntry(made_by=user, product=product, timestamp=datetime.datetime.now())
                    for product in products
                ]

                # Consider using bulk_create for efficiency
                SearchEntry.objects.bulk_create(search_entries)
            except Exception as e:
                # Log the error instead of print
                
                return JsonResponse({'error': 'Failed to create SearchEntries'}, status=500)

        return JsonResponse({'products': product_data})

    
def get_search_history(request):
    user = get_user_from_session(request)

    if user and user.is_authenticated:
        search_history = user.search_history.all()
        history_list = []

        for search_entry in search_history:
            history = {
                'timestamp': search_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'product': {
                    'id': search_entry.product.id,
                    'name': search_entry.product.name,
                    'description': search_entry.product.description,
                    'image': search_entry.product.image.url,
                },
            }
            history_list.append(history)

        return JsonResponse({"history": history_list})
    else:
        return JsonResponse({"message": "No user logged in"})
