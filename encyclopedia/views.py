from django.shortcuts import redirect, render
from django.urls import reverse
from markdown2 import Markdown
from django import forms
from django.http import HttpResponseRedirect
from random import choice


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
        """
        Shows an error if a name already exists in the database.
        """
        entry_list = util.list_entries()

        if self.data["name"].lower() in map(lambda x:x.lower(), entry_list):
            raise forms.ValidationError("Title already present in the encyclopedia")

        return self.data


class PageEdit(forms.Form):
    text = forms.CharField(
        label="Entry text",
        widget=forms.Textarea
    )


def index(request):
    """
    Renders the homepage of the website.
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry_pages(request, entry_name):
    """
    Renders an entry page based on its name.
    """
    markdowner = Markdown()

    # try to convert the markdown text
    try:
        text = markdowner.convert(util.get_entry(entry_name))
    except Exception:
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
    """
    Renders an error page.
    """
    return render(request, "encyclopedia/error_page.html")


def search_pages(request):
    """
    Searches pages based on names or prefixes of the name.
    """
    if request.method == "POST":
        entries_list = util.list_entries()
        search_argument = request.POST.get("q")

        # retrieve entries that matches parts of the given string
        substring_list = [x for x in entries_list if search_argument.lower() in x.lower()]

        # redirect the user directly or give a page with search results
        if search_argument.lower() in map(lambda x:x.lower(), entries_list):
            return redirect(f"wiki/{search_argument}")
        else:
            return render(request, "encyclopedia/search_result.html", {
                "search_results": substring_list
            })
    else:
        # show the error page if something goes wrong
        return HttpResponseRedirect(reverse("error_page"))


def add_page(request):
    """
    Adds a new page to the entries list.
    """
    if request.method == "POST":
        form = PageAdd(request.POST)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            text = form.cleaned_data.get("text")

            # save the new entry
            util.save_entry(name, text)

            # go to the new page
            return HttpResponseRedirect(f"/wiki/{name}")

        else:
            # return the same page in case of an error
            return render(request, "encyclopedia/add_page.html", {
                "form": form
            })

    # render the standard page to add a page
    return render(request, "encyclopedia/add_page.html", {
        "form": PageAdd()
    })


def edit_page(request, entry_name):
    """
    Edits an existing page.
    """
    if request.method == "POST":
        form = PageEdit(request.POST)

        if form.is_valid():
            text = form.cleaned_data.get("text")

            # save the edited entry
            util.save_entry(entry_name, text)

            # go to the edited page
            return HttpResponseRedirect(f"/wiki/{entry_name}")

        else:
            # return the same page in case of an error
            return render(request, f"encyclopedia/wiki/{entry_name}/edit_page.html", {
                "form": form
            })

    # render the standard page to edit a page
    return render(request, "encyclopedia/edit_page.html", {
        "form": PageEdit(
            initial={"text": util.get_entry(entry_name)}),
        "page_name": entry_name
    })


def random_page(request):
    """
    Renders a random page.
    """
    entries_list = util.list_entries()
    page = choice(entries_list)
    return redirect(f"wiki/{page}")
