from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.views.generic import TemplateView
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from .forms import (
    SignUpForm,
    LoginForm,
    TalkForm,
    UsernameChangeForm,  
    EmailChangeForm,
    FriendsSearchForm,
    IconChangeForm,
)
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .models import User, Talk
from django.db.models import Q
from django.urls import reverse_lazy
from django.db.models import Max
from django.db.models.functions import Greatest, Coalesce


def index(request):
    return render(request, "main/index.html")


class SignUpView(FormView):
    template_name = "main/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = auth.authenticate(self.request, username=username, password=password)
        if user:
            auth.login(self.request, user)
        return super().form_valid(form)


class LoginView(auth_views.LoginView):
    authentication_form = LoginForm  # ログイン用のフォームを指定
    template_name = "main/login.html"  # テンプレートを指定


class FriendsView(LoginRequiredMixin, ListView):
    template_name = "main/friends.html"
    paginate_by = 7
    context_object_name = "friends"

    def get_queryset(self):
        queryset = User.objects.exclude(id=self.request.user.id).annotate(
            sent_talk__time__max=Max(
                "sent_talk__time",
                filter=Q(sent_talk__receiver=self.request.user),
            ),
            received_talk__time__max=Max(
                "received_talk__time",
                filter=Q(received_talk__sender=self.request.user),
            ),
            time_max=Greatest(
                "sent_talk__time__max", "received_talk__time__max"
            ),
            last_talk_time=Coalesce(
                "time_max",
                "sent_talk__time__max",
                "received_talk__time__max",
            ),
        ).order_by("-last_talk_time")
        form = FriendsSearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            if keyword:
                queryset = queryset.filter(username__icontains=keyword)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = FriendsSearchForm(self.request.GET)
        if form.is_valid():
            context["keyword"] = form.cleaned_data["keyword"]
        context["form"] = form
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "main/settings.html"


class TalkRoomView(LoginRequiredMixin, CreateView):
    model = Talk
    form_class = TalkForm
    template_name = "main/talk_room.html"

    def dispatch(self, request, *args, **kwargs):
        # 友達ユーザーを取得（存在しない場合は404）
        self.friend = get_object_or_404(User, id=self.kwargs["user_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # トーク履歴の取得
        return Talk.objects.filter(
            Q(sender=self.request.user, receiver=self.friend)
            | Q(sender=self.friend, receiver=self.request.user)
        ).order_by("time")

    def form_valid(self, form):
        # フォームが有効なときに送信者と受信者を設定
        talk = form.save(commit=False)
        talk.sender = self.request.user
        talk.receiver = self.friend
        talk.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        # 投稿成功後のリダイレクト先
        return reverse("talk_room", kwargs={"user_id": self.friend.id})

    def get_context_data(self, **kwargs):
        # テンプレートに渡す追加データ
        context = super().get_context_data(**kwargs)
        context["friend"] = self.friend
        context["talks"] = self.get_queryset()
        return context


class UsernameChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsernameChangeForm
    template_name = "main/username_change.html"
    success_url = reverse_lazy("username_change_done")

    def get_object(self, queryset=None):
        return self.request.user


class UsernameChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = "main/username_change_done.html"


class EmailChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EmailChangeForm
    template_name = "main/email_change.html"
    success_url = reverse_lazy("email_change_done")

    def get_object(self, queryset=None):
        return self.request.user


class EmailChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = "main/email_change_done.html"


class PasswordChangeView(auth_views.PasswordChangeView):
    """Django 組み込みパスワード変更ビュー

    template_name : 表示するテンプレート
    success_url : 処理が成功した時のリダイレクト先
    """

    template_name = "main/password_change.html"
    success_url = reverse_lazy("password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """Django 標準パスワード変更ビュー"""

    template_name = "main/password_change_done.html"


class LogoutView(auth_views.LogoutView):
    pass


# @login_required
# def icon_change(request):
#     if request.method == "GET":
#         form = IconChangeForm(instance=request.user)
#     elif request.method == "POST":
#         form = IconChangeForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = request.user
#             user.icon = form.cleaned_data['icon']
#             form.save()
#             return redirect("icon_change_done")

#     context = {
#         "form": form,
#     }
#     return render(request, "main/icon_change.html", context)


# @login_required
# def icon_change_done(request):
#     return render(request, "main/icon_change_done.html")

class IconChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = IconChangeForm
    template_name = "main/icon_change.html"
    success_url = reverse_lazy("icon_change_done")

    def get_object(self, queryset=None):
        return self.request.user


class IconChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = "main/icon_change_done.html"