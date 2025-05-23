from django.shortcuts import render,redirect
from . import util
import markdown2
import random
import os

def index(request):
    #Display all entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,title):
    content = util.get_entry(title)

    if content is None:
        #Error message if entry not found
        return render(request, "encyclopedia/error.html", {
            "message": f"Page for {title} not found."
        })
    else:
        #Convert Markdown to html
        html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get('q','').strip()
    if not query:
        return redirect('index')  # Redirect to index instead of error page


    entries = util.list_entries()
    matches = [entry for entry in entries if query.lower() in entry.lower()]

    if len(matches) == 1 :
        # If exactly one match exists and matches the query exactly
        return redirect(f"/wiki/{matches[0]}")
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches
    })

def create(request):
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            return render(request, "encyclopedia/error.html", {
                "message": "Content or Title cannot be empty."
            })
        
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html", {
                "message": f"Entry with the title '{title}' already exists."
            })
        
        util.save_entry(title, content)
        return entry(request, title)  #try return redirect("/wiki/entry")

    return render(request, "encyclopedia/create.html")

def edit(request, title):
    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if not content:
            return render(request, "encyclopedia/error.html", {
                "message": "Content cannot be empty."
            })
        
        util.save_entry(title, content)
        return redirect("entry", title=title)
    
    else:
        content = util.get_entry(title)

        if content is None:
            return render(request, "encyclopedia/error.html", {
                "message": f"The requested page '{title}' does not exist."
            })
        
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": content
        })
    
def random_page(request):
    entries = util.list_entries()
    if not entries:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries found."
        })
    
    random_title  = random.choice(entries)
    return entry(request, random_title)

def delete(request, title):
    if request.method == "POST":
        # Check if the entry exists
        filepath = f"entries/{title}.md"
        if os.path.exists(filepath):
            # Delete the file
            os.remove(filepath)
            return redirect("index")
        else:
            return render(request, "encyclopedia/error.html", {
                "message": "The entry you are trying to delete does not exist."
            })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "Invalid request method. Use POST to delete entries."
        })
    