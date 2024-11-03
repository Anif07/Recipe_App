from django import forms
from .models import Recipe, Ingredient, Image, Collection
from django.forms import inlineformset_factory,modelformset_factory
from datetime import timedelta

from django import forms
from django.forms import inlineformset_factory
from datetime import timedelta

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = (
            'title', 'servings', 'preparation_time', 'total_time',
            'calories', 'instructions', 'cuisine', 'food_type', 'difficulty_level','featured'
        )
        
    def clean(self):
        cleaned_data = super().clean()
        preparation_time = cleaned_data.get('preparation_time')
        total_time = cleaned_data.get('total_time')
        
        if preparation_time is not None and total_time is not None:
            if not isinstance(preparation_time, timedelta) or not isinstance(total_time, timedelta):
                self.add_error('preparation_time', "Preparation time and total time must be valid durations.")
            elif preparation_time > total_time:
                self.add_error('preparation_time', "Preparation time must be less than or equal to total time.")

        return cleaned_data
          

class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ('name', 'quantity', 'unit', 'is_optional')

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True  
)


class RecipeImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

RecipeImageFormSet = inlineformset_factory(
    Recipe,
    Image,
    form=RecipeImageForm,
    extra=1,
    can_delete=True  
)




class CollectionCreateForm(forms.ModelForm):
    recipes = forms.ModelMultipleChoiceField(queryset=Recipe.objects.all(), required=False)

    class Meta:
        model = Collection
        fields = ['title', 'recipes']
