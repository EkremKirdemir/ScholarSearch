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
from .search import searchCorrection, search_and_parse

@require_http_methods(["GET"])
def search(request):
    # Display the search page
    return render(request, 'search.html')

def run_search(request):
    query = request.GET.get('query', '')
    corrected_query = searchCorrection(query)
    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']
    documents = list(collection.find({'keywords_se': corrected_query}))
    if len(documents) == 0:
        search_results1 = search_and_parse(corrected_query)
    # Redirect to the search results page with the corrected query as a parameter
    url = reverse('search_results') + f'?query={corrected_query}'
    return HttpResponseRedirect(url)


def search_results(request):
    print("query1")
    query = request.GET.get('query', '')
    corrected_query = searchCorrection(query)
    # search_and_parse(corrected_query)

    client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
    db = client['SearchScholar']
    collection = db['Results']

    # Fetch documents with all required fields
    documents = list(collection.find({'keywords_se': corrected_query}, {
    '_id': 1, 'paper_name': 1, 'paper_date': 1, 'paper_authors': 1, 'paper_citations': 1, 'paper_abstract': 1}))
    # print(documents[0])

    print(documents[0])
    # Paginate the results
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for document in documents:
        # print(str(document['citations']))
        document['id_str'] = str(document['_id'])

    return render(request, 'search_results.html', {'page_obj': page_obj, 'query': corrected_query})



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
    
    order_by = request.GET.get('order_by', 'default')

    if order_by == 'alphabetical':
        documents = list(collection.find({}, {'_id': 1, 'paper_name': 1}).sort('paper_name', 1))
    else:
        documents = list(collection.find({}, {'_id': 1, 'paper_name': 1}))
    for doc in documents:
        doc['id_str'] = str(doc['_id'])
    # Paginate the results
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render the homepage with the search results
    return render(request, 'home.html', {'page_obj': page_obj, 'order_by': order_by})


