from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, Thumbnail
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from ckeditor.fields import RichTextField
# Create your models here.


class Product(models.Model):
    category_choice = ( 
            ("1", "생일"),
            ("2", "가벼운 선물"),
            ("3", "건강/회복"),
            ("4", "스몰럭셔리"),
            ("5", "어른선물"),
            ("6", "크리스마스"),
            ("7", "명품선물"),
            ("8", "출산/키즈"),
            ("9", "따뜻한선물"),
            ("11", "배달선물"),
        )
    title = models.CharField(max_length=100)
    brand= models.CharField(max_length=50, null=True)
    product_url = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    category = models.CharField(max_length=2, choices=category_choice)
    price = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    like_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="like_product"
    )


class ProductImages(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    images = models.CharField(max_length=300)


class ProductContentImages(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    images = models.CharField(max_length=300)


class Review(models.Model):
    title = models.CharField(max_length=20)
    content = models.TextField()
    image = ProcessedImageField(
        upload_to="images/",
        blank=True,
        processors=[ResizeToFill(400, 300)],
        format="JPEG",
        options={"quality": 80},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    good_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="good_review"
    )
    cool_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="cool_review"
    )
    fun_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="fun_review"
    )
    sad_user = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="sad_review"
    )


class ReviewComment(models.Model):
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    review = models.ForeignKey('Review', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Community(models.Model):
    title = models.CharField(max_length=20)
    content = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_community')
    hits = models.PositiveIntegerField(default=0)
    

class CommunityImages(models.Model):
    community = models.ForeignKey("Community", on_delete=models.CASCADE)
    images = ProcessedImageField(
        upload_to="images/",
        blank=True,
        processors=[ResizeToFill(400, 300)],
        format="JPEG",
        options={"quality": 80},
    )
    
class CommunityComment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)