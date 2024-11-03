from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Recipe, Collection

def recipe_owner_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])
        if recipe.author != request.user:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def collection_owner_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.user != request.user:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view
