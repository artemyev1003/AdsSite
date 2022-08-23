from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from PIL import Image
from taggit.managers import TaggableManager


class Ad(models.Model):
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        verbose_name="Price ($)"
    )
    text = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment',
                                      related_name='comments_author')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    picture = models.ImageField(upload_to='ads_images', null=True)

    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Favs',
                                       related_name='favorite_ads')

    tags = TaggableManager(blank=True)

    # Show us in the admin list
    def __str__(self):
        return self.title

    def save(self):
        super().save()
        if self.picture:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                new_img = (400, 400)
                img.thumbnail(new_img)
                img.save(self.picture.path)


class Comment(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if len(self.text) > 15:
            return self.text[:11] + '...'
        return self.text


class Favs(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('ad', 'user')

    def __str__(self):
        return '%s likes %s' % (self.user.username, self.ad.title[:10])
