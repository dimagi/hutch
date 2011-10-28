from django import forms
from django.forms import fields

class AuxImageUploadForm(forms.Form):
    image_file  = fields.FileField()
