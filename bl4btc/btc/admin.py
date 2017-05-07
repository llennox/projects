from django.contrib import admin

from btc.models import Profil, sysvar, buyUrls, sellUrls, escrowPayoutLedger		

class AuthorAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profil, AuthorAdmin)

admin.site.register(sysvar, AuthorAdmin)

admin.site.register(buyUrls, AuthorAdmin)

admin.site.register(sellUrls, AuthorAdmin)

admin.site.register(escrowPayoutLedger, AuthorAdmin)


