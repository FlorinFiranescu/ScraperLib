from MySqlProductDatabase import *
import pandas as pd
import os
import random

class Product(object):
    productDb = None
    title = None
    price = 0
    reduced_price = 0
    link = None
    def __init__(self):
        self.title = ""
        self.price = 0
        self.reduced_price = 0
        self.link = ""

    def __str__(self):
        return f"{self.title} {self.price} {self.reduced_price} {self.link}"
