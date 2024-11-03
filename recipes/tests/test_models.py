from django.test import TestCase
from ..models import Collection,Recipe,Ingredient,Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class InitialSetup(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='anif',password='anif123')
        self.recipe=Recipe.objects.create(
            title='dosa',
            author=self.user,
            cuisine='indian',
            difficulty_level="easy",
            instructions="test instruction",
            servings=2,
            preparation_time=20,
            total_time=30,
            calories=150,
        )
        self.ingredient=Ingredient.objects.create(name='salt',quantity=100,unit='gms',recipe=self.recipe)
        self.collection= Collection.objects.create(title='test',author=self.user)
        self.collection.recipes.add(self.recipe)
        self.image=Image.objects.create(image='media/images/dosa.jpg',recipe=self.recipe)


class CollectionModelTest(InitialSetup):
    def test_collection_str(self):
        self.assertEqual(str(self.collection),'test')
        
    def test_recipe_in_collection(self):
        self.assertIn(self.recipe,self.collection.recipes.all())
        
        
class IngredientModelTest(InitialSetup):
    def test_ingredient_str(self):
        self.assertEqual(str(self.ingredient),'100 Grams salt')
        
    def test_quantity_positive(self):
        self.ingredient.quantity=0
        with self.assertRaises(ValidationError):
            self.ingredient.full_clean()
        
            
class RecipeModelTest(InitialSetup):
    def test_recipe_str(self):
        self.assertEqual(str(self.recipe),'dosa')
    
    def test_created_at(self):
        self.assertIsNotNone(self.recipe.created_at)
    
    def test_updated_at(self):
        self.recipe.title='Indian Dosa'
        self.recipe.save()
        self.assertIsNotNone(self.recipe.updated_at)
        
    def test_ingredient_in_recipe(self):
        self.assertIn(self.ingredient,self.recipe.ingredients.all())
        
    def test_preparation_totaltime(self):
        self.recipe.preparation_time=0
        with self.assertRaises(ValidationError):
            self.recipe.full_clean()
            
            
class ImageModelTest(InitialSetup):
    def test_image_str(self):
        self.assertEqual(str(self.image),'dosa-Image')
