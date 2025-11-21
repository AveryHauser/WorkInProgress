# WorkInProgress

This project is a Grocery Application for a database project. The app allows user to view food items, nutritional information, the cost of those items, and nearby grocery stores enabling them to plan their grocery trips. There will also be functionality to make grocery lists and budgets. It uses public data bases for the data used. 

This project has data from the following sources.

- `https://catalog.data.gov/dataset/food-price-outlook`
- `https://catalog.data.gov/dataset/grocery-store-locations`
- `https://catalog.data.gov/dataset/fruit-and-vegetable-prices`
- `https://catalog.data.gov/dataset/food-a-pedia`
- `https://www.ers.usda.gov/data-products/food-environment-atlas data-access-and-documentation-downloads`

This project include:

- `LICENSE` : GNU 3.0 License
- `src/data`: Folder with all of the data from different sources.
- `src/grocery_AppDB.spl` : Creating the tables and attibutes.
- Infographics

## 🛠️ How to Build, Run, and Visualize

1. **Set MySQL password**
You need to change the temp password to your MySQL password. The place holder is `CHANGE PASSWORD TO MYSQL PASSWORD`. In the files below you will need to change it on line 8 and 9 respectively.

- `src/main.py`
- `src/populate_db.py`

2. **Compile and run the project**

```bash
cd src
source venv/bin/activate
python populate_db.py
python main.py
```
