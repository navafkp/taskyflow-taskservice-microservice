from django.db import models
from django.utils.text import slugify 
import random
import string
# Create your models here.

class Boards(models.Model):
    user_id = models.IntegerField()
    workspace = models.CharField(max_length=150)
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=200)
    visibility = models.CharField(default='public', max_length=20)  # Adjust the max_length if needed
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Combine the name with a random string and some additional words
            random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            
            self.slug = slugify(f"{self.name}-{random_suffix}")

        super(Boards, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
class Columns(models.Model):
    board_id  = models.ForeignKey(Boards, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    position = models.CharField(default='1', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Card(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    board = models.ForeignKey(Boards, on_delete=models.CASCADE)
    max_members = models.IntegerField(default='1')
    created_at = models.DateTimeField(auto_now_add=True)
    column = models.CharField(default="1", null=False, max_length=15)
    color = models.CharField(max_length=100, default='#ffffff')
    priority = models.CharField(max_length=30, default='high')
    
    def __str__(self):
        return self.title
     
class Assignee(models.Model):
    user = models.EmailField()
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'card')
    
    def __str__(self):
        return self.card.title
    
    
class Comments(models.Model):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=100, default='name')
    card = models.ForeignKey(Card, on_delete = models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.comment
    
class Meeting(models.Model):
    roomID = models.CharField(max_length=255)
    description = models.TextField()
    workspace = models.CharField(max_length=255)
    organizer_id = models.CharField(max_length=255)
    starting_time = models.CharField(max_length=40)  
    expiration_time = models.CharField(max_length=2400)  
    is_active = models.BooleanField(default=True)
    password = models.CharField(default = '67ashg', max_length=100)
    
    def __str__(self) -> str:
        return self.roomID