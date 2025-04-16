from django.shortcuts import render
from rest_framework import viewsets
from .models.products import Category, Product
from .serializer import ProductSerializer,CategorySerializer



