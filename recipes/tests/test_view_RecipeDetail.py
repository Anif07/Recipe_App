from .test_models import InitialSetup
from django.urls import reverse,resolve
from ..views import RecipeDetailView

class RecipeDetailTest(InitialSetup):
    def setUp(self):
        super().setUp()
        self.recipe_detail_url=reverse('recipe:recipe_detail',kwargs={'pk':1})
        self.response=self.client.get(self.recipe_detail_url)
        
    def test_recipe_detail_status_code(self):
        self.assertEqual(self.response.status_code,200)
        
    def test_recipe_detail_url_resolve_recipe_detail_view(self):
        view=resolve('/recipe/1/')
        self.assertEqual(view.func.view_class,RecipeDetailView)
    
    def test_recipe_detail_view_not_found_status_code(self):
        self.recipe_detail_url=reverse('recipe:recipe_detail',kwargs={'pk':55})
        self.response=self.client.get(self.recipe_detail_url)
        self.assertEqual(self.response.status_code,404)
        
    def test_recipe_detail_template_used(self):
        self.assertTemplateUsed(self.response, 'recipes/recipe_detail.html')
        
    def test_recipe_detail_view_with_valid_recipe(self):
        recipe = self.response.context['recipe']
        self.assertEqual(recipe.title, 'dosa') 
        self.assertEqual(recipe.cuisine, 'indian') 