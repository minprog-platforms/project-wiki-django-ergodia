from re import search
from typing import Text
from django.shortcuts import redirect, render
from django.urls import reverse
from markdown2 import Markdown
from django import forms
from django.http import HttpResponseRedirect
from random import choice
from django.utils.safestring import mark_safe


from . import util

class PageAdd(forms.Form):
    name = forms.CharField(
        label="Name"
    )
    text = forms.CharField(
        label="Entry text",
        widget=forms.Textarea
    )

    def clean(self):
        entry_list = util.list_entries()

        if self.data["name"] in entry_list:
            raise forms.ValidationError("Title already present in the encyclopedia")
        return self.data

class PageEdit(forms.Form):
    text = forms.CharField(
        label="Entry text",
        widget=forms.Textarea
    )


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry_pages(request, entry_name):
    markdowner = Markdown()

    # try to convert the markdown text
    try:
        text = markdowner.convert(util.get_entry(entry_name))
    except:
        text = None

    # return the appropriate page
    if text is None:
        return HttpResponseRedirect(reverse("error_page"))
    else:
        return render(request, "encyclopedia/entry_pages.html", {
            "name": entry_name,
            "text": text
        })


def error_page(request):
    return render(request, "encyclopedia/error_page.html")


def search_pages(request):
    if request.method == "POST":
        entries_list = util.list_entries()
        search_argument = request.POST.get("q")
        
        substring_list = [x for x in entries_list if search_argument.lower() in x.lower()]

        if search_argument.lower() in map(lambda x:x.lower(), entries_list):
            return redirect(f"wiki/{search_argument}")
        else:
            return render(request, "encyclopedia/search_result.html", {
                "search_results": substring_list
            })
    else:
       return HttpResponseRedirect(reverse("error_page"))


def add_page(request):
    if request.method == "POST":
        form = PageAdd(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data.get("name")
            text = form.cleaned_data.get("text")
            
            # save the new entry
            util.save_entry(name, text)
            
            # go to the new page
            return redirect(f"wiki/{name}")

        else:
            return render(request, "encyclopedia/add_page.html", {
                "form": form
            })
    return render(request, "encyclopedia/add_page.html", {
        "form": PageAdd()
    })


def edit_page(request, entry_name):
    if request.method == "POST":
        form = PageEdit(request.POST)
        
        if form.is_valid():
            text = form.cleaned_data.get("text")
            
            # save the edited entry
            util.save_entry(entry_name, text)
            
            # go to the edited page
            return redirect(f"wiki/{entry_name}")

        else:
            return render(request, f"encyclopedia/wiki/{entry_name}/edit_page.html", {
                "form": form
            })
    return render(request, "encyclopedia/edit_page.html", {
        "form": PageEdit(initial={"text": util.get_entry(entry_name)})
    })


def random_page(request):
    entries_list = util.list_entries()
    page = choice(entries_list)
    return redirect(f"wiki/{page}")