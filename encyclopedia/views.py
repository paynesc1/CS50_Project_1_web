from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.core.validators import RegexValidator
import markdown2
import re
import random

from . import util

class NewEntryPage(forms.Form):
    new_title = forms.CharField(label="new_title")
    new_descr = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', "rows": "17"}) ,label="new_descr")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, title):
    entry = util.get_entry(title)
    if not entry:
        return HttpResponseNotFound('<h1>Not Found!!!!!</h>')
    entry = markdown2.markdown(entry)
    print(title)
    print(entry)
    return render(request, "encyclopedia/entry.html", {
        "title" : title,
        "entry": entry
        })

def search(request):
    if request.method == 'POST':
        #searchbar result
        query = request.POST['q']
        print(query)
        #get entry by title
        entry = util.get_entry(query)
        #if entry exists, render entry page 
        #if entry exists in get enryt, psot it and if aprt of the srach query is in get entry, post it to anpther page
        if entry:
            entry = markdown2.markdown(entry)
            return HttpResponseRedirect("encyclopedia/entry.html", {
                "title" : query
            })
        else:
            titles = util.list_entries()
            recommend = []
            for title in titles:
                if query.lower() in title.lower():
                    print(title)
                    recommend.append(title)
                    entry = markdown2.markdown(title)
                    return render(request, "encyclopedia/results.html", {
                        "title" : recommend[0]
                    })

        #if query doesn't exist, redirect to results page
        #page should have list of links whether query substring is in result

def newpage(request):
    #take input from form
    #add the entry using save
    #if entry already exists, express ERROR
    #otherwise, redirect to new entry page for the entry
    if request.method == 'GET':
        return render(request, "encyclopedia/newpage.html", {
        "form" : NewEntryPage()
        })
    if request.method == 'POST':
        form = NewEntryPage(request.POST)
        if not form.is_valid():
            return render (request, "encyclopedia/newpage.html", {
                "form" : form
            })
        new_title  = form.cleaned_data['new_title']
        new_descr = form.cleaned_data['new_descr']
        filename = f"entries/{new_title}.md"
        if default_storage.exists(filename):
            print(form)
            messages.add_message(request, messages.ERROR,'Entry already exists with the provided title!')
            return render(request, "encyclopedia/newpage.html", {
                "form": form,
            }) 
        else: 
            util.save_entry(new_title, new_descr)
            return redirect("wiki", new_title)

def edit(request, title):
    #render edit page with form
    if request.method == "GET":
        content = util.get_entry(title)
        print(content)
        return render(request, "encyclopedia/edit.html", {
            "title" : title,
            "content" : content
        })
    else:
        if request.method == 'POST':
            content = request.POST.get("descr")
            util.save_entry(title, content)
            print(title)
            print(content)
            return redirect("wiki", title)




