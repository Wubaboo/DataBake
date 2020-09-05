# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 12:42:51 2020

@author: evan
"""

import sqlite3
import pandas as pd
import datetime

def set_inventory(name, quantity):
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    cur.execute("UPDATE ingredients SET inventory_quantity = " + \
        str(quantity) + " WHERE ingredient_name = '" + name + "';")
    
    cnn.commit()
    cnn.close()
    
def add_ingredient(name, unit: str, unit_cost = 0, inventory_qty = 0):
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    sql = "INSERT INTO ingredients ("\
        "ingredient_name, inventory_quantity, unit_cost, unit) VALUES (?,?,?,?)"
    values = (name, inventory_qty, unit_cost, unit)
    cur.execute(sql, values)
    
    cnn.commit()
    cnn.close()
    
def add_expense(item, supplier, quantity = 1, category = "ingredient", unit = "unit", \
                brand = None, price = 0, note = None, date = str(datetime.datetime.now().date())):
    #Update the quantity if the purchased item is an ingredient
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    if category.lower() == "ingredient":
        cur.execute("SELECT inventory_quantity FROM ingredients" \
                       " WHERE ingredient_name = '" + item + "';")
        ret = cur.fetchall()
        if len(ret) > 0:
            new_qty = ret[0][0] + quantity
            cur.execute("UPDATE ingredients SET inventory_quantity = " + \
                           str(new_qty) + " WHERE ingredient_name ='" + item + "';")
        else:
            pp_cost = price / quantity
            add_ingredient(item, unit, pp_cost, quantity)
                   
    sql = "INSERT INTO expenses ("\
        "item, quantity, supplier, date, price, brand, category, note) VALUES (?,?,?,?,?,?,?,?)"
    values = (item, quantity, supplier, date, price, brand, category, note)
    cur.execute(sql, values)
    
    cnn.commit()
    cnn.close()

def add_product(product_type, name, price, recipe, batch_yield, note = None):
    # Recipe takes the form [(ingredient, qty), ...]
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    cost = 0
    if product_type.lower() != "set":
        df = sql_to_pd("ingredients")
        ingredients = set(df["ingredient_name"].tolist())
        #check if all the ingredients in the recipe are added
        for i in recipe:
            if i[0] not in ingredients:
                print(i[0] + " is not in the ingredients table. Add it first.")
                return
            
        add_product = "INSERT INTO products ("\
            "type, product_name, price, cost, note) VALUES (?,?,?,?,?)"
        product = (product_type, name, price, cost, note)
        cur.execute(add_product, product)
        
        #Add each ingredient to the recipe table
        for i in recipe:
            #i[0] is the ingredient name
            #i[1] is the quantity of ingredient
            unit_cost = df.at[df.index[df['ingredient_name'] == i[0]].tolist()[0], 'unit_cost']
            unit_name = df.at[df.index[df['ingredient_name'] == i[0]].tolist()[0], 'unit']
            ingredient_cost = float(unit_cost) * i[1]
            cost += ingredient_cost / batch_yield
            add_to_recipe = "INSERT INTO recipes (" \
                "product_name, ingredient_name, quantity, unit, yield, cost_per_batch, cost_per_product) VALUES (?,?,?,?,?,?,?)"
            recipe_vals = (name, i[0], i[1], unit_name, batch_yield, ingredient_cost, ingredient_cost/batch_yield)
            cur.execute(add_to_recipe, recipe_vals)
        
        # If the product is a component, also add it to the ingredient list
        if product_type.lower() == "component" and (name not in ingredients):
            #add_ingredient(name, "batch", cost, 1) - Gives locked database error because of two active cursors
            sql = "INSERT INTO ingredients ("\
            "ingredient_name, inventory_quantity, unit_cost, unit) VALUES (?,?,?,?)"
            values = (name, 1, cost, "g")
            cur.execute(sql, values)
        
        cur.execute("UPDATE products SET cost = " + \
                    str(cost) + " WHERE product_name = '" + name + "';")   

    #If the product is a set of products, find the total cost by adding the individual costs of the products
    else:
        df = sql_to_pd("products")
        products = set(df["product_name"].tolist())
        for p in recipe:
            if p[0] not in products:
                print(p[0] + " is not in the products table. Add it first.")
                return
        
        add_product = "INSERT INTO products ("\
            "type, product_name, price, cost, note) VALUES (?,?,?,?,?)"
        product = (product_type, name, price, cost, note)
        cur.execute(add_product, product)

        for p in recipe:
            unit_cost = df.at[df.index[df["product_name"] == p[0]].tolist()[0], "cost"]
            product_cost = float(unit_cost) * p[1]
            cost += product_cost/batch_yield
            add_to_recipe = "INSERT INTO recipes (" \
                "product_name, ingredient_name, quantity, unit, yield, cost_per_batch, cost_per_product) VALUES (?,?,?,?,?,?,?)"
            recipe_vals = (name, p[0], p[1], "unit", batch_yield, product_cost, product_cost/batch_yield)
            cur.execute(add_to_recipe, recipe_vals)

        cur.execute("UPDATE products SET cost = " + str(cost) + " WHERE product_name = '" + name + "';")

    cnn.commit()
    cnn.close()

def add_sale(customer, product, quantity, total, discounted = False, 
             date = str(datetime.datetime.now().date())):

    def update_inventory(cur, recipes, recipe, quantity):
        for ingredient in recipe:
            i_name = ingredient[1]
            quantity_used = ingredient[2] * quantity
            ingredients = sql_to_pd("ingredients")
            old_q = ingredients.at[ingredients.index[ingredients['ingredient_name'] == i_name].tolist()[0], 'inventory_quantity']
            new_q = old_q - quantity_used
            cur.execute("UPDATE ingredients SET inventory_quantity = " + \
                str(new_q) + " WHERE ingredient_name = '" + i_name + "';")
        
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    add_command = "INSERT INTO sales (" \
        "date, customer, product, quantity, total, discounted) VALUES (?,?,?,?,?,?)" 
    sales_values = (date, customer, product, quantity, total, discounted)
    cur.execute(add_command, sales_values)
    
    products = sql_to_pd("products")
    recipes = sql_to_pd("recipes")
    recipe = recipes.loc[recipes["product_name"] == product].values.tolist()

    #If the sale was a set of products, deduct the from the inventory of each ingredient for each product
    if products.loc[products["product_name"] == product]["type"].values.tolist()[0] == "set":
        #(set, product, quantity, unit, batch_yield, batch_cost, unit_cost)
        for (s_name, p_name, p_quant, p_units, s_batch, s_batch_cost, s_unit_cost) in recipe: 
            p_recipe = recipes.loc[recipes["product_name"] == p_name].values.tolist()
            update_inventory(cur, recipes, p_recipe, p_quant)
            
    #Otherwise, if the sale was just a product, update ingredients inventory
    else:
        update_inventory(cur, recipes, recipe, quantity)
        
    cnn.commit()
    cnn.close()
                               
def get_tables(cur):
    cnn = sqlite3.connect(r"database.db")
    cur = cnn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
    res = cur.fetchall()
    res = [s[0] for s in res][1:]
    
    cnn.close()
    return res
    
def sql_to_pd(table_name):
    cnn = sqlite3.connect(r"database.db")
    df = pd.read_sql_query("SELECT * FROM " + table_name, cnn)
    cnn.close()
    return df
