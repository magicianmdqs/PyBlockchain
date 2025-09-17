from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("blocks/", views.blocks, name="blocks"),
    path("api/tx/account/<str:address>", views.tx_account, name="tx_account"),
    path("tx/account/", views.tx_account_html, name="tx_account_html"),
    path("api/tx/<str:address>/<int:amount>",views.transfer_send,name="transfer_send"),
    path("tx/",views.transfer_send_html,name="transfer_send_html"),
    path("wallet/",views.wallet,name="wallet"),
    path("wallet/<str:address>",views.wallet_info,name="wallet_info"),
    path("search/",views.search_tx,name="search_tx"),
]
