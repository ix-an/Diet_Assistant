from django.http import JsonResponse
from .models import User

# 用户登录接口
def login(request):
    # 接收客户端提交的用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')

    # 判断用户名和密码是否为空
    if not username or not password:
        return JsonResponse({"message": "用户名或密码为空"}, status=400)

    # 检查用户是否存在
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"message": "用户不存在"}, status=400)

    # 验证密码
    if user.password != password:
        return JsonResponse({"message": "密码错误"}, status=400)

    # 构建用户的基本信息
    data = {
        "id": user.id,
        "username": user.username,
        "avatar": user.avatar,
    }

    # 登录成功，返回用户信息
    return JsonResponse({
        "status": "success",
        "message": "登录成功",
        "data": data,
    })



# 用户注册接口
def register(request):
    # 接收客户端提交的用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')

    # 存入数据库
    try:
        user = User.objects.create(username=username, password=password)
    except Exception as e:
        print("注册后端接口报错：", e)
        return JsonResponse({"message": "注册失败"}, status=400)

    return JsonResponse({
        "status": "success",
        "message": "注册成功",
        "user_id": user.id,
    })



