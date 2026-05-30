# FILE: hopehub/__init__.py
# HopeHub Core Package Management Initializer
# STRICT GUARDRAIL: Do not add any URL, routing, or view imports here 
# to prevent breaking the Django AppRegistry initialization sequence.

default_app_config = 'hopehub.apps.HopehubConfig'


from .urls import *
