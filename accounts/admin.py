from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from mptt.admin import DraggableMPTTAdmin
from .models import User

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'password1','password2', 'mobile', 'first_name', 'last_name','location', 'is_staff', 'is_active',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.active = True
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label= ("Password"),
        help_text= ("<a href=\"../password/\">CHANGE PASSWORD</a>."))

    class Meta:
        model = User
        fields = '__all__'

# @admin.register(User)
class UserAdmin(DraggableMPTTAdmin, BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    
    mptt_indent_field = "mobile"
    list_display = ('tree_actions', 'indented_title','email', 'user_role', 'user_business','first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superadmin', 'is_deleted')
    list_display_links = ('indented_title',)
    # fields = ('email', 'password', 'mobile', 'first_name', 'last_name','location','is_staff', 'is_active',)
    autocomplete_fields = ['parent']
    fieldsets = (
        ('Parent Info', {'fields': ('parent',)}),
        ('User Info', {'fields': ('email', 'password', 'mobile')}),
        ('Personal info', {'fields': ('first_name', 'last_name','location')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
    )
    search_fields = ('mobile','email',)
    ordering = ('email',)
    filter_horizontal = ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def user_business(self, obj):
        if obj.business:
            if obj.business.business:
                return obj.business.business.name                            
        else:
            print("Independent")
            return "Independent"

    user_business.short_description = 'Business' 

    def user_role(self, obj):
        if obj.business:
            if obj.business.business.agencies:
                return "Client"
            elif obj.business.business.clients:
                return "Agency"
            elif obj.field_officer:
                return "Field Officer"
        else:
            print("Independent")
            return "Independent"

    user_role.short_description = 'Role' 

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)