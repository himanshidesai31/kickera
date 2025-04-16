from  django.urls import  path
from product.views import CategoryListView, CheckoutListView, \
    CartItemAddView, CartListView, CartRemoveView, CheckoutPageView, SelectUserAddressView, CartUpdateView, \
    WishListView, AddWishListView, RemoveWishListView, ProductDetailView, AddAllToCartView, GetSubcategoriesView
from django.http import JsonResponse

urlpatterns = [
    path('category/',CategoryListView.as_view(),name='category_list'),

    # path('product/',ProductListView.as_view(),name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),

    #cart related url's
    path('cart/',CartListView.as_view(),name='cart_list'),
    path('add-cart/<int:pk>/', CartItemAddView.as_view(), name='cart_add'),
    path('remove-cart/<int:pk>/', CartRemoveView.as_view(), name='cart_remove'),
    path('update-cart/<int:pk>/', CartUpdateView.as_view(), name='cart_update'),

    #wishlist Url's
    path('wishlist',WishListView.as_view(),name='wishlist'),
    path('add-wishlist/<int:pk>/', AddWishListView.as_view(), name='add_wishlist'),
    path('remove-wishlist/<int:pk>/', RemoveWishListView.as_view(), name='remove_wishlist'),
    path('add-all-to-cart/', AddAllToCartView.as_view(), name='add_all_to_cart'),

    #product checkout related url
    path('checkout/', CheckoutPageView.as_view(), name='checkout'),
    path('shipinng-address/<int:pk>/', SelectUserAddressView.as_view(), name='check_user_address'),
    
    # API endpoints
    path('get-subcategories/', GetSubcategoriesView.as_view(), name='get_subcategories'),
    
    # Debug endpoints
    path('debug-subcategories/', lambda request: JsonResponse({
        'categories': [
            {
                'id': cat.id,
                'name': cat.category_name,
                'subcategories': [
                    {
                        'id': sub.id,
                        'name': sub.sub_category_name
                    } for sub in SubCategory.objects.filter(category=cat)
                ]
            } for cat in Category.objects.all()
        ]
    }), name='debug_subcategories'),
]