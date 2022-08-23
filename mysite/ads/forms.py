from django import forms
from .models import Ad
from .humanize import naturalsize


class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)
    picture = forms.ImageField(required=False, label="File to upload <= "+max_upload_limit_text)
    upload_field_name = 'picture'

    class Meta:
        model = Ad
        fields = ['title', 'price', 'text', 'picture', 'tags']

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error("picture", "File must be < "+str(self.max_upload_limit)+"bytes")


class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)