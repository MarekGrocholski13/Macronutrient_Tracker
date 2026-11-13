from dataclasses import dataclass
from drafter import *

set_website_title("Macronutrient Tracker")
set_site_information(
    author="Marek Grocholski",
    description=""" will take in user input for a food or category of food and will give foods that
    are similar to what was input, if what the user input is not in the data provided then an error
    message will appear prompting them to go back to the home page. The user then is able to choose
    from those list of foods and can view each food individually showing the macronutrients. The user
    is then given the option of adding the food where they must first enter a specific amount of grams
    of that food and once entered it will calculate the macronutrients of that food, update the list of
    foods, update the total macronutrients for all of the foods in the list and takes them to the site
    where they can see the new list of the foods they have added as well as the total macronutrients""",
    sources="Drafter docs, LLM's, Github and Classmates",
    planning=["CS1_Final_porject_1.pdf"],
    links=["https://github.com/prasertcbs/basic-dataset/blob/master/nutrients.csv"]
)
hide_debug_information()
set_website_framed(False)

food_data="nutrients - nutrients (3).tsv"

@dataclass
class Food:
    """
    These are the macronutrients, names and other information about each specific food in the data
    
    Attributes:
    name(str): the foods name(used to find that specific food in the search_results page)
    grams(float): the grams measured for this specific food(used later to make sure measurements are correct)
    cals(float): calories of the specific food
    protein(float): protein in the specific food
    fats(float): fats in the specific food
    fiber(float): fiber in the specific food
    carbs(float): carbohydrates in the specific food
    category(str): The food category that the food falls within(used to find a specific food in the search_results page)
    """
    name:str
    grams:float
    cals:float
    protein:float
    fats:float
    fiber:float
    carbs:float
    category:str
@dataclass
class SelectedFood:
    """
    This is the food that the user had selected
    
    Attributes:
    food(Food): this is the macronutrient breakdown and other information for the food that was selected
    desired_grams(float): this is the grams that the user types in to determine what percentage of the macronutrients the user is actually consuming
    """
    food:Food
    desired_grams:float

@dataclass
class MacroTotals:
    """
    These are the total Macros that will be displayed in the user_food_list page and will be updated
    
    Attributes:
    
    total_calories(float): sum of all the calories the user has consumed
    total_protein(float): sum of all the protein the user has consumed
    total_carbs(float): sum of all the carbs the user has consumed
    total_fats(float): sum of all the fats the user has consumed
    total_fiber(float): sum of all the fiber the user has consumed
    
    """
    total_calories:float
    total_protein:float
    total_carbs:float
    total_fats:float
    total_fiber:float

@dataclass
class State:
    """
    This dataclass is the dataclass that constantly is updating it's values depending on the users inputs
    
    Attributes:
    all_foods(list[Food]): This is every single food that the data provides
    search_query(str): the food/category that the user inputs to find their desired food
    matching_foods(list[Food]): the foods that will be displayed that have anything to do with what the user entered in the search_query
    desired_foods(list[SelectedFood]): the list of foods that will be updated when a user adds that specific food to the list and is displayed on the user_food_list page
    macro_totals(MacroTotals): all of the macro nutrients added up, updates every time a food is added, eventually is displayed on the website
    error_message(str): This is the error message that appears if a food/category they typed is not in the data
    desired_grams(str): this is the weight of the food the user consumes that the user inputs into a textbox after picking a food and uses this information to calculate the total macronutrients
    selected_food(Food): the food the user ends up picking from the matching_foods list
    """
    all_foods:list[Food]
    search_query:str
    matching_foods:list[Food]
    desired_foods:list[SelectedFood]
    macro_totals:MacroTotals
    error_message:str
    desired_grams:str
    selected_food:Food | None




def parse_food(line:str)->Food:
    """
    This function is a helper function that essentially runs through the lines
    of code in the data and makes sure that the data does not have any kind of
    weird outliers that would cause the program to not run
    
    Arguments:
    line(str): a line of data/ all of the macronutrients, the name, and the category for one food
    
    Returns:
    Food: The food without any statistics that will cause errors and is changed so that the
    rest of the code can safely and efficiently use the data
    """
    pieces=line.strip().split("\t")
    name=pieces[0]
    grams=float(pieces[2].replace(",",""))
    if pieces[3]=="8-44":
        cals=26.0
    elif pieces[3]=="":
        cals=77.0
    else:
        cals=float(pieces[3].replace(",",""))
    if pieces[4]=="t":
        protein=0.0
    else:
        protein=float(pieces[4].replace(",",""))
    if pieces[5]=="t":
       fats=0.0
    elif pieces[5]=="t'":
        fats=0.0
    else:
        fats=float(pieces[5].replace(",",""))
    if pieces[7]=="t":
        fiber=0.0
    elif pieces[7]=="a":
        fiber=0.0
    else:
        fiber=float(pieces[7].replace(",",""))
    if pieces[8]=="t":
        carbs=0.0
    else:
        carbs=float(pieces[8].replace(",",""))
    category=pieces[9]
    return Food(name, grams, cals, protein, fats, fiber, carbs, category)

def load_foods()->list[Food]:
    """
    Loads the food data from the TSV file and converts each line
    into a Food object using the parse_food() function.

    Returns:
        list[Food]: A list containing all the foods and their
        macronutrient information from the data file.
    """
    food_items=[]
    with open(food_data) as file:
        for line in file:
            food_items.append(parse_food(line))
    return food_items

FOODS=load_foods()

INITIAL_STATE = State(
    all_foods=FOODS,
    search_query="",
    matching_foods=[],
    desired_foods=[],
    macro_totals=MacroTotals(
        0.0, 0.0, 0.0, 0.0, 0.0
    ),
    error_message="",
    desired_grams="",
    selected_food=None
)

def find_foods(foods:list[Food], query:str)->list[Food]:
    """
    Finds food items that match the given query. Ignores capitalization.
    As long as the query is a substring of the food name, it is considered a match.

    Args:
        foods (list[Food]): A list of Food objects to search.
        query (str): The search query string.
    Returns:
        list[Food]: A list of Food objects that match the query.
    """
    query = query.strip()

    if query == "":
        return []

    results=[]
    query_lower=query.lower()

    for food in foods:
        if query_lower in food.name.lower():
            results.append(food)
        elif query_lower in food.category.lower():
            results.append(food)

    return results


#not finished continue working        
@route
def index(state: State) -> Page:
    """
    a route function that acts as the home page of the function that acts as the point of return,
    This will be the page that allows the user to search for foods or look at the foods
    they have already added
    
    arguments:
    state(State): allows the user to see the macrototals on the homepage
    
    returns:
    Page: gives a page that will work as the main hub allowing users to navigate to different routes
    with buttons and textboxes
    """

    return Page(
        state,
        [
            Header("Macronutrient Tracker"),

            f"Calories: {state.macro_totals.total_calories:.1f}",

            f"Protein: {state.macro_totals.total_protein:.1f}g",

            f"Carbs: {state.macro_totals.total_carbs:.1f}g",

            f"Fat: {state.macro_totals.total_fats:.1f}g",

            TextBox("search_query"),

            Button(
                "Search",
                "search"
            ),

            Button(
                "My Foods",
                "user_food_list"
            )
        ]
    )

def calculate_totals(selected_foods:list[SelectedFood])->MacroTotals:
    """
    helper function that calculates up the total macronutrients from the amount of mass of food
    and the type of food chosen
    
    arguments:
    selected_foods(list[SelectedFood]): these are all of the foods that the user
    decided to add and the mass of each food
    
    returns:
    Total macronutrients from every food added and weighed
    """
    totals=MacroTotals(0,0,0,0,0)
    
    for item in selected_foods:
        scale=item.desired_grams/item.food.grams
        
        totals.total_calories += item.food.cals * scale
        totals.total_protein += item.food.protein*scale
        totals.total_carbs += item.food.carbs*scale
        totals.total_fats += item.food.fats * scale
        totals.total_fiber += item.food.fiber * scale
    return totals
        

@route
def add_food(state: State, desired_grams: str) -> Page:
    """
    This route function protects the rest of the program if any kind of unwanted user input is given,
    however, the main use of this function is that it serves as a page that will add the food chosen
    to the list of desired_foods that will be displayed later on another page as long as the mass of
    the food is provided, additionally the page shows the data points necessary for that specific food
    
    arguments:
    state(State): this acts as the selected food that the user has picked in order to add to the list,
    the macronutrients for the picked food, is used for the user inputs that is provided when asked for
    the mass of the food used, and is used to update the food list
    desired_grams(str): this is the mass that the user inputs that is then used for calculating the total macronutrients
    """
    food = state.selected_food

    if food is None:
        state.error_message = "Please select a food first."
        return index(state)

    try:
        grams = float(desired_grams)
    except (ValueError, TypeError):
        state.error_message = "Please enter a valid number of grams."
        return view_food(state, food.name)

    if grams <= 0:
        state.error_message = "Grams must be greater than zero."
        return view_food(state, food.name)

    # Create a SelectedFood object using the selected food
    # and the number of grams entered by the user.
    selected_food = SelectedFood(
        food=food,
        desired_grams=grams
    )

    # Add the food to the user's list.
    state.desired_foods.append(selected_food)

    # Recalculate all macronutrient totals.
    state.macro_totals = calculate_totals(
        state.desired_foods
    )

    # Clear the input and any previous error.
    state.desired_grams = ""
    state.error_message = ""

    # Return the updated food list.
    return user_food_list(state)



@route
def search(state: State, search_query:str) -> Page:
    """
    This route function acts as the page that displays all of the foods that are similar to whatever food
    the user may have typed in, it also allows the user to click on the view button that lets the user see the details
    of the food they clicked on.
    
    Arguments:
    state(State): The list of foods that will show up after a food/caterogory is being entered on the index page
    that are similar to what was entered, also is the value that is being updated to show the specific chosen foods macronutrients
    search_query
    """
    state.search_query = search_query


    results = find_foods(
        state.all_foods,
        search_query
    )

    if not results:
        return no_food_found_page(state)

    rows = []

    for food in results:

        rows.append(
            Row(
                food.name,
                Button(
                    "View Food",
                    "view_food",
                    arguments=[Argument("food_name",food.name)]
                )
            )
        )

    return Page(
        state,
        [
            Header("Search Results")
        ]
        + rows +
        [
            Button("Back", "index")
        ]
    )


@route
def view_food(state: State, food_name: str) -> Page:
    """
    Displays the details of the food selected by the user,
    including its serving size, calories, protein, carbohydrates,
    fats, and fiber. Allows the user to enter a desired amount
    in grams and add the food to their list.

    Args:
        state (State): The current application state, used to
            access the available foods and store the selected food.
        food_name (str): The name of the food selected by the user.

    Returns:
        Page: A page displaying the selected food's nutritional
            information and options to add the food or return home.
            If the food cannot be found, returns the no-results page.
    """
    food = None

    for item in state.all_foods:
        if item.name == food_name:
            food = item
            break

    # Handle the case where the food cannot be found
    if food is None:
        return no_food_found_page(state)

    # Store the selected food in the state
    state.selected_food = food

    return Page(
        state,
        [
            Header(food.name),

            f"Serving Size: {food.grams} g",
            f"Calories: {food.cals}",
            f"Protein: {food.protein} g",
            f"Carbs: {food.carbs} g",
            f"Fat: {food.fats} g",
            f"Fiber: {food.fiber} g",

            "Enter desired grams:",

            TextBox("desired_grams"),

            Button(
                "Add Food",
                "add_food",
            ),

            Button(
                "Back",
                "index",
            )
        ]
    )

@route
def user_food_list(state:State)->Page:
    """
    Displays the foods the user has added, the amount in grams
    of each food, and the total macronutrients for all selected foods.

    Args:
        state (State): The current application state containing
            the user's selected foods and their quantities.

    Returns:
        Page: A page displaying the selected foods, their
            nutritional information, the combined macronutrient
            totals, and a button to return to the home page.
    """
    totals = calculate_totals(state.desired_foods)

    food_rows = []

    for item in state.desired_foods:

        scale = item.desired_grams / item.food.grams

        food_rows.append(
            Row(
                f"{item.food.name}",
                f"{item.desired_grams} g",
                f"Calories: {item.food.cals * scale:.1f}",
                f"Protein: {item.food.protein * scale:.1f}",
                f"Carbs: {item.food.carbs * scale:.1f}",
                f"Fat: {item.food.fats * scale:.1f}"
            )
        )

    return Page(
        state,
        [
            Header("My Foods"),

            f"Calories: {totals.total_calories:.1f}",
            f"Protein: {totals.total_protein:.1f}g",
            f"Carbs: {totals.total_carbs:.1f}g",
            f"Fat: {totals.total_fats:.1f}g",
            f"Fiber: {totals.total_fiber:.1f}g",
        ]
        + food_rows +
        [
            Button("Back", "index")
        ]
    )

def no_food_found_page(state:State)->Page:
    """
    Displays a page informing the user that no matching food
    was found and suggesting that they try a different food
    or category.

    Args:
        state (State): The current application state, which is
            passed to the page so the user can return home.

    Returns:
        Page: A page displaying a no-results message and a
            button to return to the home page.
    """
    return Page(
        state,
        [
            Header("No results found"),
            "Try a different food or category",
            Button("Home","index"),
        ],
    )
print("Program Loaded Succesfully")




start_server(INITIAL_STATE)
