from django.test import TestCase
from django.urls import reverse,resolve
from ..views import RecipeListView
from .test_models import InitialSetup

class RecipeListTest(InitialSetup):
    def setUp(self):
        super().setUp()
        self.recipes_url=reverse('recipe:recipe_list')
        self.response=self.client.get(self.recipes_url)    
           
    def test_recipe_list_success_status_code(self):
        self.assertEqual(self.response.status_code,200)
        
    def test_recipe_list_url_resolves_recipe_list_view(self):
        view=resolve('/recipes/')
        self.assertEqual(view.func.view_class,RecipeListView)
        
    def test_recipe_list_view_contains_navigation_links(self):
        url=reverse('recipe:recipe_detail',kwargs={'pk':1})
        self.assertContains(self.response,'href="{0}"'.format(url))
        
    def test_recipe_list_uses_correct_template(self):
        url=reverse('recipe:recipe_list')
        self.response = self.client.get(url)
        self.assertTemplateUsed(self.response,'recipes/recipe_list.html')