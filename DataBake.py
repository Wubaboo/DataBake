
#GUI Imports
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTableView\
    , QHBoxLayout, QVBoxLayout, QLineEdit, QDateEdit, QCheckBox, QLabel, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QDateTime, QAbstractTableModel
from PyQt5.QtGui import QDoubleValidator
from PyQt5 import QtSql

#Plotting Imports
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

#Basic Imports
import sys
import pandas as pd
import random
import numpy as np
import datetime

#Other
import database

# Table Model Shamelessly Taken from: https://www.learnpyqt.com/courses/model-views/qtableview-modelviews-numpy-pandas/
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

# Window to display the desired table (ingredients, expenses, sales, recipes, products)
class TableWindow(QMainWindow):
    def __init__(self, table = "ingredients"):
        super(TableWindow, self).__init__()
        self.setWindowTitle(table)
        self.setGeometry(200,200, 1200,500)
        self.table = QTableView()
        df = database.sql_to_pd(table)
        self.model = TableModel(df)
        self.table.setModel(self.model)

        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.table)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Window to add Items to Database
class AddWindow(QMainWindow):
    def __init__(self, table = "expense"):
        super(AddWindow, self).__init__()
        self.setWindowTitle("Add " + table)
        self.setGeometry(200,200, 400, 500) 
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        intrestrict = QDoubleValidator()
        
        if table == "expense":
            self.name = QLineEdit(placeholderText = "Item")
            self.name.setMaximumWidth(500)
            self.brand = QLineEdit(placeholderText = "Brand")
            self.brand.setMaximumWidth(500)
            self.category = QLineEdit(placeholderText = "ingredient/equipment")
            self.category.setMaximumWidth(500)
            self.quantity = QLineEdit(placeholderText = "Quantity")
            self.quantity.setMaximumWidth(500)
            self.unit = QLineEdit(placeholderText = "unit (g,ml,unit...)")
            self.unit.setMaximumWidth(500)
            self.quantity.setMaximumWidth(500)
            self.supplier = QLineEdit(placeholderText = "supplier")
            self.supplier.setMaximumWidth(500)
            self.note = QLineEdit(placeholderText = "Note")
            self.note.setMaximumHeight(500)
            self.note.setMaximumWidth(500)

            self.date = QDateEdit()
            self.date.setDateTime(QDateTime.currentDateTime())
            self.date.setMaximumWidth(500)

            self.price = QLineEdit(placeholderText = 'Cost ($)')
            self.price.setMaximumWidth(500)
            self.price.setValidator(intrestrict)
            self.button = QPushButton("Add Expense")
            #self.button.clicked.connect(lambda: database.add_expense(self.name.text(), \
            #    self.supplier.text(), float(self.quantity.text()), self.category.text(), \
            #    self.unit.text(), self.brand.text(), float(self.price.text()), self.note.text(), self.date.text()))
            self.button.clicked.connect(self.click_expense)
            self.expenses_layout()

        elif table == "sale":
            self.date = QDateEdit()
            self.date.setDateTime(QDateTime.currentDateTime())
            self.date.setMaximumWidth(400)

            self.customer = QLineEdit(placeholderText = "Customer")
            self.customer.setMaximumWidth(500)
            self.product = QLineEdit(placeholderText = "Product")
            self.product.setMaximumWidth(500)
            self.quantity = QLineEdit(placeholderText = "Quantity")
            self.total = QLineEdit(placeholderText = "Total")
            self.total.setValidator(intrestrict)
            self.discount = QCheckBox("Discounted")
            
            self.button = QPushButton("Add Sale")
            self.button.clicked.connect(self.click_sale)
            self.sales_layout()
        
        elif table == "product":
            self.type = QLineEdit(placeholderText = "Category (Bread, Pastry...)")
            self.type.setMaximumWidth(500)
            self.name = QLineEdit(placeholderText = "Product Name")
            self.name.setMaximumWidth(500)
            self.price = QLineEdit(placeholderText  = "Price")
            self.price.setMaximumWidth(500)
            self.price.setValidator(intrestrict)
            # Recipe must be inputted as comma separated values
            # Each new ingredient must be on a new line
            self.recipe = QTextEdit(placeholderText = "Recipe (Ingredient, Quantity)")
            self.recipe.setMaximumWidth(700)
            self.recipe.setMaximumHeight(1000)
            self.batch_yield = QLineEdit(placeholderText = "Batch Yield (in g or unit)")
            self.batch_yield.setMaximumWidth(500)
            self.batch_yield.setValidator(intrestrict)
            self.note = QLineEdit(placeholderText = "Note")
            self.note.setMaximumWidth(700)
            self.note.setMaximumHeight(500)
            self.button = QPushButton("Add Product")
            #self.button.clicked.connect(lambda: database.add_product(self.type.text(),\
            #    self.name.text(), float(str(self.price.text())), self.read_recipe(self.recipe.toPlainText()), \
            #        float(str(self.batch_yield.text())), self.note.text()))
            self.button.clicked.connect(self.click_product)
            self.products_layout()

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def click_expense(self):
        database.add_expense(self.name.text(), \
                self.supplier.text(), float(self.quantity.text()), self.category.text(), \
                self.unit.text(), self.brand.text(), float(self.price.text()), self.note.text(), self.date.text())
        self.close()
    
    def click_sale(self):
        database.add_sale(self.customer.text(), \
                self.product.text(), float(self.quantity.text()), float(self.total.text()),\
                self.discount.isChecked(), self.date.text())
        self.close()

    def click_product(self):
        database.add_product(self.type.text(),\
                self.name.text(), float(str(self.price.text())), self.read_recipe(self.recipe.toPlainText()), \
                float(str(self.batch_yield.text())), self.note.text())
        self.close()
        
    def expenses_layout(self):
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.brand)
        self.layout.addWidget(self.category)
        self.layout.addWidget(self.quantity)
        self.layout.addWidget(self.unit)
        self.layout.addWidget(self.supplier)
        self.layout.addWidget(self.price)
        self.layout.addWidget(self.date)
        self.layout.addWidget(self.note)
        self.layout.addWidget(self.button)
    
    def sales_layout(self):
        self.layout.addWidget(self.date)
        self.layout.addWidget(self.customer)
        self.layout.addWidget(self.product)
        self.layout.addWidget(self.quantity)
        self.layout.addWidget(self.total)
        self.layout.addWidget(self.discount)
        self.layout.addWidget(self.button)

    def read_recipe(self, text):
        text_by_line = text.split("\n")
        print(text_by_line)
        ret = []
        for s in text_by_line:
            if "," in s:
                line = s.split(",")
                ing = line[0].strip()
                quantity = float(line[1].strip())
                add = (ing, quantity)
                ret.append(add)
        return ret
            
    def products_layout(self):
        self.layout.addWidget(self.type)
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.price)
        self.layout.addWidget(self.recipe)
        self.layout.addWidget(self.batch_yield)
        self.layout.addWidget(self.note)
        self.layout.addWidget(self.button)

# Window to display Batch Calculations
class BatchWindow(QMainWindow):
    def __init__(self, recipe, batch_quantity = 1.0):
        super(BatchWindow, self).__init__() 
        self.batch_quantity = batch_quantity
        self.df = database.sql_to_pd("recipes")
        self.df = self.df[self.df["product_name"] == recipe]
        self.df["quantity/product"] = self.df["quantity"]/self.df["yield"]
        self.df["total_amount"] = self.df["quantity/product"] * batch_quantity
        self.df["total_cost"] = self.df["cost_per_product"] * batch_quantity
        self.df = self.df[["product_name", "ingredient_name", "quantity/product", "total_amount", "unit", "cost_per_product", "total_cost"]]

        self.cost = self.df["total_cost"].sum()
        self.label = QLabel("The total cost to make " + str(batch_quantity) + " " + recipe + "(s) is " + str(self.cost))
        
        self.setWindowTitle(recipe + " batch")
        self.setGeometry(200,200, 1200, 600)
        self.table = QTableView()
        self.model = TableModel(self.df)
        self.table.setModel(self.model)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.label)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Plotting Graphs
class Plot(QVBoxLayout):
    def __init__(self):
        super(Plot, self).__init__()
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)
        
        # Buttons
        self.line = QPushButton("Sales and Expenses")
        self.line.clicked.connect(self.plotline)

        self.bar = QPushButton("Prices and Costs")
        self.bar.clicked.connect(lambda: self.plotbar())

        self.summary = QPushButton("Best and Worst Sales")
        self.summary.clicked.connect(lambda: self.plotsummary())

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.line)
        self.buttonLayout.addWidget(self.bar)
        self.buttonLayout.addWidget(self.summary)

        self.addWidget(self.canvas)
        self.addLayout(self.buttonLayout)
        self.plotline()

    def plotline(self):
        self.ax.clear()
        expenses = database.sql_to_pd("expenses")
        sales = database.sql_to_pd("sales")
        expenses_grouped = expenses.groupby(["date"])["price"].sum().reset_index()
        sales_grouped = sales.groupby(["date"])["total"].sum().reset_index()
        merged = expenses_grouped.merge(sales_grouped, on = "date", how = "outer")
        merged.fillna(value = 0, inplace = True)
        merged.sort_values(by = "date", inplace = True)
        print(merged)
        sns.lineplot(x = "date", y = "price", ax = self.ax, data = merged)
        sns.lineplot(x = "date", y = "total", ax = self.ax, data = merged, color = "red").set_title("Sales and Expenses")
        self.ax.legend(labels = ["expenses", "sales"])
        self.ax.set_xticklabels(labels= merged["date"].tolist(), rotation= 45, ha='right')
        self.figure.canvas.draw_idle()

    def plotbar(self, n = 3):
        self.ax.clear()
        products = database.sql_to_pd("products")
        products = products.loc[(products["type"] != "component") & (products["type"] != "set")]
        products["diff"] = products["price"] - products["cost"]
        large = products.nlargest(n , 'diff')
        small = products.nsmallest(n, 'diff')
        res = pd.concat([large, small]).sort_index()
        res = pd.melt(res, id_vars = ["product_name"], value_vars = ["price","cost"])
        sns.barplot(x = "product_name", y = "value", hue = "variable", data = res, ax = self.ax).set_title("Product Prices and Costs")
        self.figure.canvas.draw_idle()

    def plotsummary(self, n = 2):
        self.ax.clear()
        sales = database.sql_to_pd("sales")
        grouped = sales.groupby(["product"]).sum().reset_index()
        print(grouped)

        #nlargest = grouped.groupby("product")["total"].nlargest(n).reset_index()['level_1'].values
        #nsmallest = grouped.groupby("product")["total"].nsmallest(n).reset_index()['level_1'].values
        nlargest = grouped.nlargest(n, "total")
        nsmallest = grouped.nsmallest(n, "total")

        res = pd.concat([nlargest, nsmallest]).sort_index()
        sns.barplot(x = "product", y = "total", data = res, ax = self.ax).set_title("Best and Worst Product Sales")
        self.figure.canvas.draw_idle()        

# Main Window
class Bake(QMainWindow):
    def __init__(self):
        super(Bake, self).__init__()
        self.setGeometry(200,200, 1100, 1100) 
        self.layout()

    def layout(self):
        #View Tables Buttons
        self.viewTableLabel = QLabel("View Tables:")
        self.viewTableLabel.setMaximumWidth(200)
        self.ingredientsTable = QPushButton("View Ingredients")
        self.ingredientsTable.clicked.connect(lambda: self.displayTable("ingredients"))
    
        self.salesTable = QPushButton("View Sales")
        self.salesTable.clicked.connect(lambda: self.displayTable("sales"))

        self.expensesTable = QPushButton("View Expenses")
        self.expensesTable.clicked.connect(lambda: self.displayTable("expenses"))

        self.recipesTable = QPushButton("View Recipes")
        self.recipesTable.clicked.connect(lambda: self.displayTable("recipes"))

        self.productsTable = QPushButton("View Products")
        self.productsTable.clicked.connect(lambda: self.displayTable("products"))
        
        #Add View_Tables_Buttons to Layout
        tableRow = QHBoxLayout()
        tableRow.addWidget(self.viewTableLabel)
        tableRow.addWidget(self.ingredientsTable)
        tableRow.addWidget(self.salesTable)
        tableRow.addWidget(self.expensesTable)
        tableRow.addWidget(self.recipesTable)
        tableRow.addWidget(self.productsTable)

        # Add Buttons
        self.addLabel = QLabel("Add to Database:")
        self.addLabel.setMaximumWidth(200)
        self.addProduct = QPushButton("Add Product")
        self.addProduct.clicked.connect(lambda: self.addItem("product"))
        self.addSale = QPushButton("Add Sale")
        self.addSale.clicked.connect(lambda: self.addItem("sale"))
        self.addExpense = QPushButton("Add Expense")
        self.addExpense.clicked.connect(lambda: self.addItem("expense"))

        addRow = QHBoxLayout()
        addRow.addWidget(self.addLabel)
        addRow.addWidget(self.addProduct)
        addRow.addWidget(self.addSale)
        addRow.addWidget(self.addExpense)

        # Batch Calculator
        products = database.sql_to_pd("products")
        products = products.loc[products["type"] != "set"]["product_name"].values.tolist()

        self.batchLabel = QLabel("Batch Calculator:")
        self.batchLabel.setMaximumWidth(200)
        self.batchRecipe = QComboBox(self)
        self.batchRecipe.addItems(products)
        self.batchRecipe.setMaximumWidth(400)
        intrestrict = QDoubleValidator()
        self.batchQuantity = QLineEdit(placeholderText = "Batch Quantity")
        self.batchQuantity.setValidator(intrestrict)
        self.batchQuantity.setMaximumWidth(150)
        self.checkBatch = QPushButton("Batch Values")
        self.checkBatch.clicked.connect(lambda: self.displayBatch(str(self.batchRecipe.currentText()), \
            self.batchQuantity.text()))
        
        batchRow = QHBoxLayout()
        batchRow.addWidget(self.batchLabel)
        batchRow.addWidget(self.batchRecipe)
        batchRow.addWidget(self.batchQuantity)
        batchRow.addWidget(self.checkBatch)

        # Graphs
        self.graphs = Plot()

        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(tableRow)
        mainLayout.addLayout(addRow)
        mainLayout.addLayout(batchRow)
        mainLayout.addLayout(self.graphs)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def addItem(self, table):
        self.window = AddWindow(table)
        self.window.show()

    def displayTable(self, table):
        self.table = TableWindow(table)
        self.table.show()
    
    def displayBatch(self, product, quantity):
        if quantity != "":
            self.batch = BatchWindow(product, float(quantity))
            self.batch.show()

def main():
    app = QApplication(sys.argv)
    main = Bake()
    main.setWindowTitle("DataBake")
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
