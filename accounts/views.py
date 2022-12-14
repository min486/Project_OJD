from django.shortcuts import render, redirect, get_object_or_404
from accounts.forms import SignupForm, UpdateForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime
import time

# Create your views here.


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = request.POST.get("username")
            user.email = request.POST.get("username")
            age_range = (datetime.today().year - user.birth_date.year) // 10
            if age_range < 0 or age_range > 15:
                messages.error(request, "유효한 생년월일이 아닙니다.")
                return redirect("articles:index")
            user.age = age_range
            user.save()
            auth_login(
                request, user, backend="django.contrib.auth.backends.ModelBackend"
            )
        else:
            messages.error(request, "유효하지 않은 정보입니다.")
        return redirect("articles:index")
    else:
        form = SignupForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/signup.html", context)


def login(request):
    if request.user.is_anonymous:
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                auth_login(request, form.get_user())
                return redirect(request.GET.get("next") or "articles:index")
            else:
                messages.warning(request, "아이디 혹은 비밀번호가 틀렸습니다.")
                return redirect("accounts:login")
        else:
            form = AuthenticationForm()

        context = {
            "form": form,
        }
        return render(request, "accounts/login.html", context)
    else:
        return redirect("articles:index")


@login_required
def logout(request):
    auth_logout(request)
    return redirect("accounts:login")


@login_required
def update(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = UpdateForm(request.POST, request.FILES, instance=request.user)
            print(form)
            if form.is_valid():
                form.save()
                messages.success(request, "수정되었습니다.")
            else:
                messages.warning(request, "유효하지 않은 양식입니다.")
            return redirect("accounts:detail", request.user.pk)
        else:
            form = UpdateForm(instance=request.user)
        context = {
            "form": form,
        }
        return render(request, "accounts/update.html", context)
    else:
        messages.warning(request, "로그인 후 이용할 수 있습니다.")
        return redirect("accounts:login")


@login_required
def delete(request):
    if request.method == "POST":
        request.user.delete()
        auth_logout(request)
        messages.success(request, "성공적으로 탈퇴되었습니다.")
    return redirect("articles:index")


@login_required
def password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, "변경되었습니다.")
            return redirect("accounts:update")
        else:
            form = PasswordChangeForm(request.user)
        context = {
            "form": form,
        }
        return render(request, "accounts/password.html", context)
    else:
        messages.warning(request, "로그인 후 이용할 수 있습니다.")
        return redirect("accounts:login")


def detail(request, user_pk):
    user = get_object_or_404(get_user_model(), pk=user_pk)

    posts = user.community_set.all().order_by("-id")
    posts_page = request.GET.get("page", "1")  # GET 방식으로 정보를 받아오는 데이터
    posts_paginator = Paginator(posts, "3")  # Paginator(분할될 객체, 페이지 당 담길 객체수)
    paginated_posts = posts_paginator.get_page(posts_page)

    review_list = user.review_set.all().order_by("-id")  # 데이터 역순 정렬
    page = request.GET.get("page", "1")  # GET 방식으로 정보를 받아오는 데이터
    paginator = Paginator(review_list, "4")  # Paginator(분할될 객체, 페이지 당 담길 객체수)
    paginated_review_list = paginator.get_page(page)  # 페이지 번호를 받아 해당 페이지를 리턴

    wishlist = user.like_product.all().order_by("-id")
    wishlist_page = request.GET.get("page", "1")  # GET 방식으로 정보를 받아오는 데이터
    wishlist_paginator = Paginator(wishlist, "3")  # Paginator(분할될 객체, 페이지 당 담길 객체수)
    paginated_wishlist = wishlist_paginator.get_page(wishlist_page)

    context = {
        "user": user,
        "paginated_post_list": paginated_posts,
        "paginated_review_list": paginated_review_list,
        "paginated_wishlist": paginated_wishlist,
    }
    return render(request, "accounts/detail.html", context)


def follow(request, user_pk):
    if request.user.is_authenticated:
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if request.user != user:
            if user.followers.filter(pk=request.user.pk).exists():
                user.followers.remove(request.user)
                is_followed = False
            else:
                user.followers.add(request.user)
                is_followed = True
            context = {
                "is_followed": is_followed,
                "followings_count": user.following.count(),
                "followers_count": user.followers.count(),
            }
            return JsonResponse(context)
        else:
            messages.error(request, "자신은 팔로우할 수 없습니다.")
        return redirect("accounts:detail", user_pk)
    else:
        messages.warning(request, "로그인 후 이용할 수 있습니다.")
        return redirect("accounts:login")


def block(request, user_pk):
    if request.user.is_authenticated:
        user = get_object_or_404(get_user_model(), pk=user_pk)
        if request.user != user:
            if user.blockers.filter(pk=request.user.pk).exists():
                user.blockers.remove(request.user)
                is_blocked = False
            else:
                user.blockers.add(request.user)
                is_blocked = True
            context = {
                "is_blocked": is_blocked,
            }
            return JsonResponse(context)
        else:
            messages.error(request, "자신은 차단할 수 없습니다.")
        return redirect("accounts:detail", user_pk)
    else:
        messages.warning(request, "로그인 후 이용할 수 있습니다.")
        return redirect("accounts:login")


def wishlist(request, user_pk):
    context = {
        "user": get_object_or_404(get_user_model(), pk=user_pk),
    }
    return render(request, "accounts/wishlist.html", context)
