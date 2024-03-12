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
    order_by = request.GET.get('order_by', 'default')

    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']
    
    query_filters = {'keywords_se': corrected_query}

    for field in ['paper_name', 'paper_authors', 'paper_abstract', 'paper_publisher_name', 'keywords_paper', 'publisher_type']:
        user_input = request.GET.get(field)
        if user_input:
            query_filters[field] = {"$regex": user_input, "$options": "i"}

    if order_by == 'alphabetical':
        documents = list(collection.find(query_filters).sort('paper_name', 1))
    elif order_by == 'citations':
        documents = list(collection.find(query_filters))
        documents = sorted(
    documents,
    key=lambda x: (
        x['paper_citations'] == 'unknown',
        int(x['paper_citations'].replace(',', '').replace('.', '')) if x['paper_citations'] != 'unknown' else 0
    ),
    reverse=True
)
    elif order_by == 'date':
        documents = list(collection.find(query_filters))
        documents = sorted(documents, key=lambda x: (x.get('paper_date', '').split()[-1] if x.get('paper_date', '').split()[-1].isdigit() else '9999', x.get('paper_date', '')))
    else:
        documents = list(collection.find(query_filters))
    
    paginator = Paginator(documents, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for document in documents:
        document['id_str'] = str(document['_id'])

    return render(request, 'search_results.html', {
        'page_obj': page_obj,
        'query': corrected_query,
        'order_by': order_by,
    })



def paper_detail(request, object_id):
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']

    document = collection.find_one({'_id': ObjectId(object_id)})

    return render(request, 'paper_detail.html', {'document': document})

@require_http_methods(["GET"])
def home(request):
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']

    order_by = request.GET.get('order_by', 'default')
    query = request.GET.get('query', '')
    paper_name = request.GET.get('paper_name', '')
    paper_authors = request.GET.get('paper_authors', '')
    paper_abstract = request.GET.get('paper_abstract', '')
    paper_publisher = request.GET.get('paper_publisher', '')
    keywords = request.GET.get('keywords', '')
    publisher_type = request.GET.get('publisher_type', '')

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

    documents = list(collection.find(query_filters))

    if order_by == 'date':
        def extract_year(doc):
            year_match = re.search(r'\b(19|20)\d{2}\b', doc.get('paper_date', ''))
            if year_match:
                return int(year_match.group(0))
            return 9999 if doc.get('paper_date', '') == 'unknown' else 10000

        documents.sort(key=extract_year)
    elif order_by == 'citations':
        documents = sorted(
    documents,
    key=lambda x: (
        x['paper_citations'] == 'unknown',
        int(x['paper_citations'].replace(',', '').replace('.', '')) if x['paper_citations'] != 'unknown' else 0
    ),
    reverse=True
)
    elif order_by == 'alphabetical':
        documents.sort(key=lambda x: x.get('paper_name', '').lower())

    for doc in documents:
        doc['id_str'] = str(doc['_id'])

    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'order_by': order_by,
        'current_filters': {
            'query': query,
            'paper_name': paper_name,
            'paper_authors': paper_authors,
            'paper_abstract': paper_abstract,
            'paper_publisher': paper_publisher,
            'keywords': keywords,
            'publisher_type': publisher_type,
        },
        'request': request
    })


