import uuid
import os
from django.utils.safestring import mark_safe
from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="catgories")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name
    class Meta:
        verbose_name_plural = "Categories"


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.size_name


class Product(BaseModel):
    parent = models.ForeignKey(
        'self', related_name='variants', on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    product_desription = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True)
    size_variant = models.ManyToManyField(SizeVariant, blank=True)
    newest_product = models.BooleanField(default=False)
    trending_product = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.product_name

    def get_product_price_by_size(self, size):
        return self.price + SizeVariant.objects.get(size_name=size).price

    def get_rating(self):
        total = sum(int(review['stars']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0
    def get_absolute_url(self):
        return reverse("get_product", kwargs={"slug": self.slug})


def upload_to_random(instance, filename):
   
    #Renames uploaded file to a random UUID while keeping extension.
    
    ext = filename.split('.')[-1]  # get file extension
    new_filename = f"{uuid.uuid4().hex}.{ext}"  # generate random name
    return os.path.join('product', new_filename)  # save inside 'product/' folder

class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to=upload_to_random)

    # ✅ add flags
    is_featured = models.BooleanField(default=False)
    show_in_slider = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Ensure exclusivity
        if self.is_featured:
            self.show_in_slider = False
        elif self.show_in_slider:
            self.is_featured = False
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.product.product_name
    @classmethod
    def slider_images(cls):
        return cls.objects.filter(show_in_slider=True)

    @classmethod
    def featured_images(cls):
        return cls.objects.filter(is_featured=True)

    def img_preview(self):
        return mark_safe(f'<img src="{self.image.url}" width="500"/>')



class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_amount = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    stars = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_reviews", blank=True)

    def like_count(self):
        return self.likes.count()

    def dislike_count(self):
        return self.dislikes.count()


class Wishlist(BaseModel):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    size_variant=models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True,
                                     blank=True, related_name="wishlist_items")

    added_on=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user', 'product', 'size_variant')

    def __str__(self) -> str:
        return f'{self.user.username} - {self.product.product_name} - {self.size_variant.size_name if self.size_variant else "No Size"}'
