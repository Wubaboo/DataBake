# DataBake
GUI and Database for baking needs. `database.py` uses sqlite3 to interact with `database.db`. `databake.py` is the GUI.

![databake screenshot](https://github.com/Wubaboo/DataBake/blob/master/screenshot.png?raw=true)

### Baking Recipes 
The `products` table in database.db keeps track of all products (final products, product components, and sets of products), their costs to produce, and their selling price.
The `recipes` table keeps track of the ingredients needed for each of the products in the `products` table, and their costs per batch.
   
### Inventory Management
`ingredients` table keeps track of ingredients in inventory and their unit costs. 

### Batch Calculation
The batch calculator displays a table of the quantity of ingredients required to produce a given number of a product (for final products and product components) and the total cost to produce the batch. 
- Select the desired product in the `Batch Calculator` drop down list. 
- Input desired quantity and press the `Batch Values` button. 

### Sales and Expenses
Sales and Expenses are recorded in their respective tables. Ingredient inventory quantities are affected appropriately.

### Visualizations
Basic Visualizations are displayed in the GUI.
- Overview of Expenses and Sales over time
- Highest and lowest profit margins for top 3 and bottom 3 products
- Best and worst selling products

## Adding Data
- All data in `database.db` should be removed prior to usage.
-	The `Add Expense` button in the GUI adds an expense to the `expense` table. Typing "ingredient" in the "ingredient/equipemnt" input line will also add the ingredient to the `ingredients` table if it does not already exist, or update the inventory_quantity of the ingredient if the ingredient is already in the table.
- The `Add Sale` button adds a sale to the `sales` table and deducts inventory quantity from each ingredient in the `ingredients` table
- The `Add Product` button adds a product to the `products` table and its recipe to the `recipes` table.
	- The product `type` can be "set" or "component"
		- A `set` product is a collection of final products (such as an assorted party tray)
		- A `component` is an incomplete product that is used as ingredients for other products. These are also added to the `ingredients` table. 
	- each ingredient in the recipe should be on a new row. The format to add a recipe is:
		
		ingredient1_name, ingredient1_quantity
		
		ingredient2_name, ingredient2_quantity
		
		...
		
	- Units should be in the same units listed in the `ingredients` table. (Most units are g and ml)

