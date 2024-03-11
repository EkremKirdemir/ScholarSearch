import subprocess
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from pymongo import MongoClient
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from bson import ObjectId
from django.shortcuts import redirect
import pymongo
from .search import searchCorrection, search_and_parse
import re

@require_http_methods(["GET"])
def search(request):
    # Display the search page
    return render(request, 'search.html')

@require_http_methods(["GET"])
def run_search(request):
    query = request.GET.get('query', '')
    corrected_query = searchCorrection(query)
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']
    documents = list(collection.find({'keywords_se': corrected_query})) 
    if len(documents) == 0 or documents is None:
        search_results1 = search_and_parse(corrected_query)
    url = reverse('search_results') + f'?query={corrected_query}'
    return HttpResponseRedirect(url)

@require_http_methods(["GET"])
def search_results(request):
    query = request.GET.get('query', '')
    corrected_query = searchCorrection(query)

    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']
    
    query_filters = {'keywords_se': corrected_query}
    # print(request.GET['paper_name'])
    # Add more filters based on user input
    for field in ['paper_name', 'paper_authors', 'paper_abstract', 'paper_publisher_name', 'keywords_paper', 'publisher_type']:
        user_input = request.GET.get(field)
        print(user_input)
        if user_input:
            query_filters[field] = {"$regex": user_input, "$options": "i"}
    documents = list(collection.find(query_filters, {
        '_id': 1, 'paper_name': 1, 'paper_date': 1, 'paper_authors': 1, 
        'paper_citations': 1, 'paper_abstract': 1, 'paper_publisher_name': 1,
        'keywords_se': 1, 'keywords_paper': 1, 'publisher_type': 1
    }))
    # order_by = request.GET.get('order_by', 'default')

    # if order_by == 'alphabetical':
    #     documents = list(collection.find({'keywords_se': corrected_query}, {
    # '_id': 1, 'paper_name': 1, 'paper_date': 1, 'paper_authors': 1, 'paper_citations': 1, 'paper_abstract': 1}).sort('paper_name', 1))
    # else:
    #     documents = list(collection.find({'keywords_se': corrected_query}, {
    # '_id': 1, 'paper_name': 1, 'paper_date': 1, 'paper_authors': 1, 'paper_citations': 1, 'paper_abstract': 1}))
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for document in documents:
        # print(str(document['citations']))
        document['id_str'] = str(document['_id'])

    return render(request, 'search_results.html', {'page_obj': page_obj, 'query': corrected_query,})



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
    # Database setup
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']

    # Retrieve filters and order_by value from the request
    order_by = request.GET.get('order_by', 'default')
    query = request.GET.get('query', '')
    paper_name = request.GET.get('paper_name', '')
    paper_authors = request.GET.get('paper_authors', '')
    paper_abstract = request.GET.get('paper_abstract', '')
    paper_publisher = request.GET.get('paper_publisher', '')
    keywords = request.GET.get('keywords', '')
    publisher_type = request.GET.get('publisher_type', '')

    # Build query filters based on user input
    query_filters = {}
    if query:
        query_filters['keywords_se'] = {"$regex": query, "$options": "i"}
    if paper_name:
        query_filters['paper_name'] = {"$regex": paper_name, "$options": "i"}
    if paper_authors:
        query_filters['paper_authors'] = {"$regex": paper_authors, "$options": "i"}
    if paper_abstract:
        query_filters['paper_abstract'] = {"$regex": paper_abstract, "$options": "i"}
    if paper_publisher:
        query_filters['paper_publisher_name'] = {"$regex": paper_publisher, "$options": "i"}
    if keywords:
        query_filters['keywords_paper'] = {"$regex": keywords, "$options": "i"}
    if publisher_type:
        query_filters['publisher_type'] = publisher_type

    # Apply sorting if 'alphabetical' is selected
    documents = list(collection.find(query_filters))

    # Custom Python sorting if 'date' is selected
    if order_by == 'date':
        def extract_year(doc):
            year_match = re.search(r'\b(19|20)\d{2}\b', doc.get('paper_date', ''))
            if year_match:
                return int(year_match.group(0))
            return 9999 if doc.get('paper_date', '') == 'unknown' else 10000  # 'unknown' sorts before other non-year values

        documents.sort(key=extract_year)

    elif order_by == 'alphabetical':
        documents.sort(key=lambda x: x.get('paper_name', '').lower())

    # Assign string IDs for use in templates
    for doc in documents:
        doc['id_str'] = str(doc['_id'])

    # Pagination
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the page with filtered and sorted results
    return render(request, 'home.html', {
        'page_obj': page_obj,
        'order_by': order_by,
        # Include the current filters in the context to repopulate the form
        'current_filters': {
            'query': query,
            'paper_name': paper_name,
            'paper_authors': paper_authors,
            'paper_abstract': paper_abstract,
            'paper_publisher': paper_publisher,
            'keywords': keywords,
            'publisher_type': publisher_type,
        },
        'request': request  # Pass the request to maintain form state
    })


