from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView,DetailView,FormView
from .models import Collection,Recipe,Ingredient,Image
from django.core.paginator import Paginator
from django.forms import modelformset_factory
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import inlineformset_factory
from .forms import RecipeForm, RecipeIngredientFormSet, RecipeImageFormSet,CollectionCreateForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from .decorators import recipe_owner_required,collection_owner_required
import json

def home_page(request):
    return render(request,'home.html')
    

class RecipeListView(ListView):
    model=Recipe
    template_name='recipe_list.html'
    context_object_name='recipes'
    paginate_by=3
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        featured_recipes=Recipe.objects.filter(featured=True)
        paginator=Paginator(featured_recipes,6)
        page_number=self.request.GET.get('featured_page')
        context['featured_recipes_page']=paginator.get_page(page_number)
        return context


class RecipeDetailView(DetailView):
    model=Recipe
    template_name='recipes/recipe_detail.html'
    context_object_name='recipe'

class CollectionListView(ListView):
    model=Collection
    template_name='collection/collections.html'
    context_object_name='collections'

class CollectionDetailView(DetailView):
    model=Collection
    template_name='collection/collection_detail.html'
    context_object_name='collection'

class CollectionCreateView(CreateView):
    model = Collection
    template_name = 'collection/collection_form.html'
    form_class = CollectionCreateForm
    success_url = reverse_lazy('recipe:collection_list')  # Redirect to the collection list after creation

    def form_valid(self, form):
        form.instance.author = self.request.user  # Set the author to the logged-in user
        return super().form_valid(form)

class CollectionUpdateView(UpdateView):
    model=Collection
    template_name='collection/collection_form.html'
    form_class=CollectionCreateForm
    context_object_name='collection'

    def get_queryset(self):
        return Collection.objects.filter(author=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('recipe:collection_detail',kwargs={'pk':self.object.pk})
    
class CollectionDeleteView(DeleteView):
    model = Collection
    template_name = 'collection/collection_confirm_delete.html'
    context_object_name = 'collection'
    success_url = reverse_lazy('recipe:collection_list')  # Redirect after deletion

    # Limit delete permission to the author
    def get_queryset(self):
        return Collection.objects.filter(author=self.request.user)

class RecipeCreateView(LoginRequiredMixin,FormView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/create_recipe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredient_formset'] = RecipeIngredientFormSet(self.request.POST, prefix='ingredients')
            context['image_formset'] = RecipeImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        else:
            context['ingredient_formset'] = RecipeIngredientFormSet(prefix='ingredients')
            context['image_formset'] = RecipeImageFormSet(prefix='images')
        return context

    def form_valid(self, form):
        recipe = form.save(commit=False)
        recipe.author = self.request.user
        recipe.save()

        ingredient_formset = RecipeIngredientFormSet(self.request.POST, prefix='ingredients')

        if ingredient_formset.is_valid():
            ingredients = ingredient_formset.save(commit=False)
            for ingredient in ingredients:
                ingredient.recipe = recipe 
                ingredient.save()
        else:
            print(ingredient_formset.errors)  

        image_formset = RecipeImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        
        if image_formset.is_valid():
            images = image_formset.save(commit=False)
            for image in images:
                image.recipe = recipe  
                image.save()
        else:
            print(image_formset.errors)  

        return redirect('recipe:recipe_detail', pk=recipe.pk)
    
    def form_invalid(self, form):
        ingredient_formset = RecipeIngredientFormSet(self.request.POST, prefix='ingredients')
        image_formset = RecipeImageFormSet(self.request.POST, self.request.FILES, prefix='images')
        
        initial_ingredients = [
            {
                'id': ingredient.cleaned_data.get('id', ''),
                'name': ingredient.cleaned_data.get('name', ''),
                'quantity': ingredient.cleaned_data.get('quantity', ''),
                'unit': ingredient.cleaned_data.get('unit', ''),
                'is_optional': ingredient.cleaned_data.get('optional', False)
            }
            for ingredient in ingredient_formset.forms if ingredient.is_valid() and not ingredient.cleaned_data.get('DELETE', False)
        ]
       
        initial_images = [
            {
                'id': image.cleaned_data.get('id', ''),
                'url': ''
            }

            for image in image_formset.forms if image.is_valid() and not image.cleaned_data.get('DELETE', False)
        ]
        
        ingredient_formset = RecipeIngredientFormSet(self.request.POST, initial=initial_ingredients, prefix='ingredients')
        image_formset = RecipeImageFormSet(self.request.POST,self.request.FILES, initial=initial_images, prefix='images')

        return self.render_to_response({
            'form': form,
            'ingredient_formset': ingredient_formset,
            'image_formset': image_formset,
            'initial_ingredients': json.dumps(initial_ingredients),
            'initial_images': json.dumps(initial_images),
        })
            
            
@method_decorator(recipe_owner_required, name='dispatch')           
class RecipeUpdateView(UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/create_recipe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        context['ingredient_formset'] = RecipeIngredientFormSet(
            instance=recipe, prefix='ingredients'
        )
        context['image_formset'] = RecipeImageFormSet(
            instance=recipe, prefix='images'
        )
        context['initial_ingredients'] = json.dumps([
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'is_optional': ingredient.optional,
            } for ingredient in recipe.ingredients.all()
        ])
        context['initial_images'] = json.dumps([
            {
                'id': image.id,
                'url': image.image.url, 
            } for image in recipe.images.all()
        ])
        context['recipe'] = recipe
        return context

    def form_valid(self, form):
        recipe = form.save(commit=False)
        recipe.author = self.request.user  
        recipe.save()

        ingredient_formset = RecipeIngredientFormSet(self.request.POST, instance=recipe, prefix='ingredients')
        if ingredient_formset.is_valid():
            ingredient_formset.save() 
        else:
            print(ingredient_formset.errors)

        image_formset = RecipeImageFormSet(self.request.POST, self.request.FILES, instance=recipe, prefix='images')
        if image_formset.is_valid():
            image_formset.save()  
        else:
            print(image_formset.errors,"image")
            
        return redirect('recipe:recipe_detail', pk=recipe.pk)

    def form_invalid(self, form):
        ingredient_formset = RecipeIngredientFormSet(self.request.POST, instance=self.object, prefix='ingredients')
        image_formset = RecipeImageFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='images')
        initial_ingredients = json.dumps([
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'is_optional': ingredient.optional,
            } for ingredient in form.instance.ingredients.all()
        ])
        initial_images = json.dumps([
            {
                'id': image.id,
                'url': image.image.url, 
            } for image in form.instance.images.all()
        ])
        recipe = self.object
        return self.render_to_response({
            'form': form,
            'ingredient_formset': ingredient_formset,
            'image_formset': image_formset,
            'initial_ingredients':initial_ingredients,
            'initial_images':initial_images,
            'recipe':recipe
        })


@method_decorator(recipe_owner_required, name='dispatch')           
class RecipeDeleteView(DeleteView):
    model = Recipe
    template_name = 'recipes/recipe_confirm_delete.html'  
    context_object_name = 'recipe'
    success_url = reverse_lazy('recipe:recipe_list')  

    def get_queryset(self):
        return super().get_queryset()
