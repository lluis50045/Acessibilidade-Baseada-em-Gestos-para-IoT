from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from boto3.dynamodb.conditions import Key
from django.contrib.auth import logout
from autenticao.models import Conta 
from django.utils.decorators import method_decorator
from django.views import View
import boto3
from boto3.dynamodb.conditions import Attr
import json
from django.http import JsonResponse
import requests
from dashboard.models import GestoRegistrado

    
@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # 1. Buscar a Conta do usuário logado
    try:
        conta = Conta.objects.get(user=request.user)
    except Conta.DoesNotExist:
        return render(request, 'home2.html', {'erro': 'Conta não encontrada.'})

    gestos_registrados = GestoRegistrado.objects.filter(usuario=request.user)
    gestos_dict = {g.gesto: g.nome for g in gestos_registrados}
    
    amazon_id = conta.amazon_user_id
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
    table = dynamodb.Table('SmartHomeVirtualButtonsPython') 

            # 3. Buscar itens no DynamoDB que tenham o mesmo amazon_user_id
    response = table.scan(FilterExpression=Attr('lwaRealUserId').eq(amazon_id))
    items = response.get('Items', [])
    if not items:
        checked = False
    else:
        checked = True
    # Fazendo o split da lista de gestos
    todos_gestos = "Vitoria, Aberta, Joia, dislike, amor, fechado, Apontando"
    lista_gestos = [g.strip() for g in todos_gestos.split(",")]
    print("GESTOS REGISTRADOS:", gestos_dict)

    context = {
        'nome': conta.nome,
        'amazon_id': conta.amazon_user_id,
        'email': conta.email,
        'gestos_registrados': gestos_dict,
        'lista_gestos': lista_gestos, 
        'checked': checked,
    }

    return render(request, 'home2.html', context)
    

def notFound(request):
    return render(request, '404.html', status=404)
def logout_view(request):
    
    logout(request)
    return redirect('principal')


class RegistrarGestoView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            gesture = data.get("gesture")
            name = data.get("name")
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({"error": "Não autenticado"}, status=401)
            try:
                conta = Conta.objects.get(user=request.user)
            except Conta.DoesNotExist:
                return render(request, 'home2.html', {'erro': 'Conta não encontrada.'})
            amazon_id = conta.amazon_user_id
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
            table = dynamodb.Table('SmartHomeVirtualButtonsPython') 

            # 3. Buscar itens no DynamoDB que tenham o mesmo amazon_user_id
            response = table.scan(
                FilterExpression=Attr('lwaRealUserId').eq(amazon_id)
            )
            items = response.get('Items', [])
            for item in items:
                user_id = item.get("userId")

            # Headers com Authorization
            headers = {
                'Authorization': 'sua-senha-api-padrao-aqui',  # substitua pela sua senha real
                'Content-Type': 'application/json',
            }

            response = requests.post(
                'https://d1ivl6cbzb.execute-api.us-east-1.amazonaws.com/default/AlexaVirtualButtonsSkillPython',
                headers=headers,
                json={
                    "command": "setname",
                    "userId": user_id,
                    "param1": gesture,
                    "param2": name
                }
            )
            GestoRegistrado.objects.create(
            usuario=user,
            nome=name,
            gesto=gesture
        )
            if response.status_code == 200:
                
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Erro na API externa", "details": response.text}, status=500)

        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
        
        
class deletarGesto(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            gesture = data.get("gesture")
            name = data.get("name")
            user = request.user

            if not user.is_authenticated:
                return JsonResponse({"error": "Não autenticado"}, status=401)
            try:
                conta = Conta.objects.get(user=request.user)
            except Conta.DoesNotExist:
                return render(request, 'home2.html', {'erro': 'Conta não encontrada.'})
            amazon_id = conta.amazon_user_id
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
            table = dynamodb.Table('SmartHomeVirtualButtonsPython') 

            # 3. Buscar itens no DynamoDB que tenham o mesmo amazon_user_id
            response = table.scan(
                FilterExpression=Attr('lwaRealUserId').eq(amazon_id)
            )
            items = response.get('Items', [])
            for item in items:
                user_id = item.get("userId")

            # Headers com Authorization
            headers = {
                'Authorization': 'sua-senha-api-padrao-aqui',  # substitua pela sua senha real
                'Content-Type': 'application/json',
            }
            print(gesture)
            print(user_id)
            response = requests.post(
                'https://d1ivl6cbzb.execute-api.us-east-1.amazonaws.com/default/AlexaVirtualButtonsSkillPython',
                headers=headers,
                json={
                    "command": "deletebutton",
                    "userId": user_id,
                    "param1": gesture,
                }
            )
        #     GestoRegistrado.objects.create(
        #     usuario=user,
        #     nome=name,
        #     gesto=gesture
        # )
            if response.status_code == 200:
                GestoRegistrado.objects.filter(usuario=user, gesto=gesture).delete()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Erro na API externa", "details": response.text}, status=500)

        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
        
        
def get_gestos_por_usuario(request):
    amazon_user_id = request.GET.get('amazon_user_id')

    if not amazon_user_id:
        return HttpResponse("Amazon User ID não fornecido.", status=400)

    try:
        conta = Conta.objects.get(amazon_user_id=amazon_user_id)
    except Conta.DoesNotExist:
        return HttpResponse("Conta não encontrada.", status=404)

    gestos = GestoRegistrado.objects.filter(usuario=conta.user)
    data = {
        "gestures": {
            g.gesto: g.nome for g in gestos
        }
    }

    return JsonResponse(data)
    
