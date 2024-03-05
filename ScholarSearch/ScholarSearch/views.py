from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from bson import ObjectId

@require_http_methods(["GET"])
def search(request):
    # Display the search page
    return render(request, 'search.html')

def paper_detail(request, object_id):
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']

    # Fetch the document by its _id
    document = collection.find_one({'_id': ObjectId(object_id)})

    # Render a template with the document details
    return render(request, 'paper_detail.html', {'document': document})
@require_http_methods(["GET"])
def home(request):
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']
    
    # Fetch all documents from the MongoDB collection
    documents = list(collection.find({}, {'paper_name': 1}))  # Only fetch the paper_name field
    for doc in documents:
        doc['id_str'] = str(doc['_id'])
    # Paginate the results
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the homepage with the search results
    return render(request, 'home.html', {'page_obj': page_obj})

@require_http_methods(["GET"])
def search_results(request):
    # Get the search query from the GET request
    query = request.GET.get('query', '')

    # TODO: Perform the search using your search engine logic and get the results

    # Render the search results page with the results
    # For now, it just returns the query as a simple HttpResponse
    return HttpResponse(f"Search results for: {query}")

# Make sure to map these views to URLs in your urls.py
