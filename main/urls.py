from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("friends/", views.FriendsView.as_view(), name="friends"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("talk_room/<user_id>", views.TalkRoomView.as_view(), name="talk_room"),
    path("username_change/", views.UsernameChangeView.as_view(), name="username_change"),
    path(
        "username_change_done/", views.UsernameChangeDoneView.as_view(), name="username_change_done"
    ),
    path("email_change/", views.EmailChangeView.as_view(), name="email_change"),
    path("email_change_done/", views.EmailChangeDoneView.as_view(), name="email_change_done"),
    path(
        "password_change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change_done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # path("icon_change/", views.icon_change, name="icon_change"),
    # path("icon_change_done/", views.icon_change_done, name="icon_change_done"),
    path("icon_change/", views.IconChangeView.as_view(), name="icon_change"),
    path("icon_change_done/", views.IconChangeDoneView.as_view(), name="icon_change_done"),
]
