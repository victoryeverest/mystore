from django.db.models import Q
from django.shortcuts import render
from products.models import Product, Category,ProductImage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.


def index(request):
    query = Product.objects.all()  # only 10 products
    categories = Category.objects.all()
    selected_sort = request.GET.get('sort')
    selected_category = request.GET.get('category')
    slider_images = ProductImage.slider_images()
    featured_images = ProductImage.featured_images()
  

    if selected_category:
        query = query.filter(category__category_name=selected_category)

    if selected_sort:
        if selected_sort == 'newest':
            query = query.filter(newest_product=True).order_by('category_id')
        elif selected_sort == 'priceAsc':
            query = query.order_by('price')
        elif selected_sort == 'priceDesc':
            query = query.order_by('-price')

    query = query[:10]
     
    page = request.GET.get('page', 1)
    paginator = Paginator(query, 20)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    except Exception as e:
        print(e)

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'selected_sort': selected_sort,
        "slider_images":slider_images,
        "featured_images":featured_images


    }
    return render(request, 'core/index.html', context)


def product_search(request):
    query = request.GET.get('q', '')

    if query:
        # Search for products that contain the query string in their product_name field
        products = Product.objects.filter(Q(product_name__icontains=query) | Q(
            product_name__istartswith=query))
    else:
        products = Product.objects.none()

    context = {'query': query, 'products': products}
    return render(request, 'core/search.html', context)


def contact(request):
    context = {"form_id": "xgvvlrvn"}
    return render(request, 'core/contact.html', context)


def about(request):
    return render(request, 'core/about.html')


