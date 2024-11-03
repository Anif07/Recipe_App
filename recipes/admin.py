from django.contrib import admin
from .models import Collection,Recipe,Ingredient,Image

class ImageInline(admin.TabularInline):
    model=Image
    extra=1
    
class IngredientInline(admin.TabularInline):
    model=Ingredient
    extra=2

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ordering=['-created_at']
    inlines=[ImageInline,IngredientInline]

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    pass
