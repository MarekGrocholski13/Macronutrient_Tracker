from dataclasses import dataclass
from drafter import *
from bakery import assert_equal

set_website_title("Macronutrient Tracker")
set_site_information(
    author="Marek Grocholski",
    description="""will take in user input for a food or category of food
and will give foods that are similar to what was input, if what
the user input is not in the data provided then an error message
will appear prompting them to go back to the home page. The user
then is able to choose from those list of foods and can view each
food individually showing the macronutrients. The user is then
given the option of adding the food where they must first enter a
specific amount of grams of that food and once entered it will
calculate the macronutrients of that food, update the list of
foods, update the total macronutrients for all of the foods in the
list and takes them to the site where they can see the new list of
the foods they have added as well as the total macronutrients""",
    sources="Drafter docs, LLM's, Github and Classmates",
    planning=["CS1_Final_porject_1.pdf"],
    links=["https://github.com/prasertcbs/basic-dataset/blob/master/nutrients.csv"]
)

try:
    hide_debug_information()
except Exception:
    pass

set_website_framed(False)

food_data = "nutrients - nutrients (3).tsv"

@dataclass
class Food:
    """
    These are the macronutrients, names and other information about
    each specific food in the data
    
    Attributes:
    name(str): the foods name(used to find that specific food
    in the search_results page)
    grams(float): the grams measured for this specific food
    (used later to make sure measurements are correct)
    cals(float): calories of the specific food
    protein(float): protein in the specific food
    fats(float): fats in the specific food
    fiber(float): fiber in the specific food
    carbs(float): carbohydrates in the specific food
    category(str): The food category that the food falls within
    (used to find a specific food in the search_results page)
    """
    name: str
    grams: float
    cals: float
    protein: float
    fats: float
    fiber: float
    carbs: float
    category: str

@dataclass
class SelectedFood:
    """
    This is the food that the user had selected
    
    Attributes:
    food(Food): this is the macronutrient breakdown and other
    information for the food that was selected
    desired_grams(float): this is the grams that the user types
    in to determine what percentage of the macronutrients the
    user is actually consuming
    """
    food: Food
    desired_grams: float

@dataclass
class MacroTotals:
    """
    These are the total Macros that will be displayed in the
    user_food_list page and will be updated
    
    Attributes:
    total_calories(float): sum of all the calories the user consumed
    total_protein(float): sum of all the protein the user consumed
    total_carbs(float): sum of all the carbs the user consumed
    total_fats(float): sum of all the fats the user consumed
    total_fiber(float): sum of all the fiber the user consumed
    """
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fats: float
    total_fiber: float

@dataclass
class State:
    """
    This dataclass constantly updates its values depending
    on the user inputs
    
    Attributes:
    all_foods(list[Food]): This is every single food data provides
    search_query(str): the food/category input to find desired food
    matching_foods(list[Food]): the foods that will be displayed
    that have anything to do with what the user entered
    desired_foods(list[SelectedFood]): the list of foods updated
    when a user adds a specific food to the list
    macro_totals(MacroTotals): all of the macro nutrients added up,
    updates every time a food is added
    error_message(str): error message that appears if food not found
    desired_grams(str): weight of food user consumes inputted into
    textbox after picking a food
    selected_food(Food): the food user ends up picking from matching
    high_protein_filter(bool): Checkbox state for filtering protein
    """
    all_foods: list[Food]
    search_query: str
    matching_foods: list[Food]
    desired_foods: list[SelectedFood]
    macro_totals: MacroTotals
    error_message: str
    desired_grams: str
    selected_food: Food | None
    high_protein_filter: bool


def parse_food(line: str) -> Food:
    """
    This function is a helper function that essentially runs
    through the lines of code in the data and makes sure that
    the data does not have any kind of weird outliers that
    would cause the program to not run
    
    Arguments:
    line(str): a line of data/ all of the macronutrients, the name,
    and the category for one food
    
    Returns:
    Food: The food without any statistics that will cause errors
    and is changed so that the rest of the code can safely use it
    """
    pieces = line.strip().split("\t")
    name = pieces[0]
    grams = float(pieces[2].replace(",", ""))
    if pieces[3] == "8-44":
        cals = 26.0
    elif pieces[3] == "":
        cals = 77.0
    else:
        cals = float(pieces[3].replace(",", ""))
    if pieces[4] == "t":
        protein = 0.0
    else:
        protein = float(pieces[4].replace(",", ""))
    if pieces[5] == "t":
        fats = 0.0
    elif pieces[5] == "t'":
        fats = 0.0
    else:
        fats = float(pieces[5].replace(",", ""))
    if pieces[7] == "t":
        fiber = 0.0
    elif pieces[7] == "a":
        fiber = 0.0
    else:
        fiber = float(pieces[7].replace(",", ""))
    if pieces[8] == "t":
        carbs = 0.0
    else:
        carbs = float(pieces[8].replace(",", ""))
    category = pieces[9]
    return Food(
        name, grams, cals, protein, fats, fiber, carbs, category
    )

def load_foods() -> list[Food]:
    """
    Loads the food data from the TSV file and converts each line
    into a Food object using the parse_food() function.

    Returns:
        list[Food]: A list containing all the foods and their
        macronutrient information from the data file.
    """
    food_items = []
    try:
        with open(food_data) as file:
            for line in file:
                food_items.append(parse_food(line))
    except FileNotFoundError:
        pass
    return food_items

FOODS = load_foods()

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
    selected_food=None,
    high_protein_filter=False
)

def find_foods(
    foods: list[Food], query: str, high_protein_only: bool = False
) -> list[Food]:
    """
    Finds food items that match the given query. Ignores capitalization.
    As long as the query is a substring of the food name, it matches.

    Args:
        foods (list[Food]): A list of Food objects to search.
        query (str): The search query string.
        high_protein_only (bool): Optional flag to filter items.
    Returns:
        list[Food]: A list of Food objects that match the query.
    """
    query = query.strip()

    if query == "":
        return []

    results = []
    query_lower = query.lower()

    for food in foods:
        matches = (query_lower in food.name.lower()) or \
                  (query_lower in food.category.lower())
        if matches:
            if high_protein_only and food.protein < 10.0:
                continue
            results.append(food)

    return results


@route
def index(state: State) -> Page:
    """
    a route function that acts as the home page of the function
    that acts as the point of return, This will be the page that
    allows the user to search for foods or look at the foods
    they have already added
    
    arguments:
    state(State): allows the user to see the macrototals on home
    
    returns:
    Page: gives a page that will work as the main hub allowing
    users to navigate to different routes with buttons and textboxes
    """
    error_display = f"Error: {state.error_message}" \
                    if state.error_message else ""
    state.error_message = ""

    return Page(
        state,
        [
            Header("Macronutrient Tracker"),
            error_display,
            f"Calories: {state.macro_totals.total_calories:.1f}",
            f"Protein: {state.macro_totals.total_protein:.1f}g",
            f"Carbs: {state.macro_totals.total_carbs:.1f}g",
            f"Fat: {state.macro_totals.total_fats:.1f}g",
            TextBox("search_query"),
            CheckBox(
                "high_protein_filter",
                label="High Protein Only (>= 10g)"
            ),
            Button("Search", "search"),
            Button("My Foods", "user_food_list")
        ]
    )

def calculate_totals(selected_foods: list[SelectedFood]) -> MacroTotals:
    """
    helper function that calculates up the total macronutrients
    from the amount of mass of food and the type of food chosen
    
    arguments:
    selected_foods(list[SelectedFood]): these are all of the foods
    that the user decided to add and the mass of each food
    
    returns:
    Total macronutrients from every food added and weighed
    """
    totals = MacroTotals(0, 0, 0, 0, 0)
    
    for item in selected_foods:
        scale = item.desired_grams / item.food.grams
        
        totals.total_calories += item.food.cals * scale
        totals.total_protein += item.food.protein * scale
        totals.total_carbs += item.food.carbs * scale
        totals.total_fats += item.food.fats * scale
        totals.total_fiber += item.food.fiber * scale
    return totals
        

@route
def add_food(state: State, desired_grams: str) -> Page:
    """
    This route function protects the rest of the program if any kind
    of unwanted user input is given, however, the main use of this
    function is that it serves as a page that will add the food
    chosen to the list of desired_foods that will be displayed
    later on another page as long as the mass of the food is
    provided, additionally the page shows data points necessary
    
    arguments:
    state(State): this acts as the selected food that the user
    has picked in order to add to the list, the macronutrients
    for the picked food, is used for user inputs that is provided
    when asked for the mass, and is used to update the food list
    desired_grams(str): this is the mass that the user inputs that
    is then used for calculating the total macronutrients
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

    selected_food = SelectedFood(
        food=food,
        desired_grams=grams
    )

    state.desired_foods.append(selected_food)

    state.macro_totals = calculate_totals(
        state.desired_foods
    )

    state.desired_grams = ""
    state.error_message = ""

    return user_food_list(state)



@route
def search(
    state: State, search_query: str, high_protein_filter: bool = False
) -> Page:
    """
    This route function acts as the page that displays all of the
    foods that are similar to whatever food the user may have
    typed in, it also allows the user to click on the view button
    that lets the user see the details of the food they clicked on.
    
    Arguments:
    state(State): The list of foods that will show up after a
    food/category is entered on index page similar to what was
    entered, also is the value being updated to show macros
    search_query
    """
    state.search_query = search_query
    state.high_protein_filter = high_protein_filter

    results = find_foods(
        state.all_foods,
        search_query,
        high_protein_filter
    )

    if not results:
        return no_food_found_page(state)

    rows = []

    for food in results:
        rows.append(
            Row(
                f"{food.name} - Protein: {food.protein}g",
                Button(
                    "View Food",
                    "view_food",
                    arguments=[Argument("food_name", food.name)]
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
            access available foods and store selected food.
        food_name (str): The name of the food selected by user.

    Returns:
        Page: A page displaying the selected food's nutritional
            information and options to add the food or return home.
            If the food cannot be found, returns no-results page.
    """
    food = None

    for item in state.all_foods:
        if item.name == food_name:
            food = item
            break

    if food is None:
        return no_food_found_page(state)

    state.selected_food = food
    error_display = f"Error: {state.error_message}" \
                    if state.error_message else ""
    state.error_message = ""

    return Page(
        state,
        [
            Header(food.name),
            error_display,
            f"Serving Size: {food.grams} g",
            f"Calories: {food.cals}",
            f"Protein: {food.protein} g",
            f"Carbs: {food.carbs} g",
            f"Fat: {food.fats} g",
            f"Fiber: {food.fiber} g",
            "Enter desired grams:",
            TextBox("desired_grams"),
            Button("Add Food", "add_food"),
            Button("Back", "index")
        ]
    )

@route
def user_food_list(state: State) -> Page:
    """
    Displays the foods the user has added, the amount in grams
    of each food, and the total macronutrients for all selected foods.

    Args:
        state (State): The current application state containing
            the user's selected foods and their quantities.

    Returns:
        Page: A page displaying the selected foods, their
            nutritional information, combined macronutrient totals,
            and a button to return to the home page.
    """
    totals = calculate_totals(state.desired_foods)

    food_rows = []

    for item in state.desired_foods:
        scale = item.desired_grams / item.food.grams

        food_rows.append(
            Row(
                f"{item.food.name} ({item.desired_grams} g)",
                f"Cal: {item.food.cals * scale:.1f}",
                f"P: {item.food.protein * scale:.1f}g",
                f"C: {item.food.carbs * scale:.1f}g",
                f"F: {item.food.fats * scale:.1f}g",
                Button(
                    "Delete",
                    "delete_food",
                    arguments=[Argument("food_name", item.food.name)]
                )
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
            Button("Clear All", "clear_foods"),
            Button("Back", "index")
        ]
    )

def no_food_found_page(state: State) -> Page:
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
            Button("Home", "index"),
        ],
    )

@route
def delete_food(state: State, food_name: str) -> Page:
    """
    Deletes a specific selected food from the user's added food list 
    and updates the accumulated macro totals.
    """
    updated_foods = []
    for item in state.desired_foods:
        if item.food.name != food_name:
            updated_foods.append(item)
            
    state.desired_foods = updated_foods
    state.macro_totals = calculate_totals(state.desired_foods)
    return user_food_list(state)

@route
def clear_foods(state: State) -> Page:
    """
    Clears all added food items and resets macro totals.
    """
    state.desired_foods = []
    state.macro_totals = MacroTotals(0.0, 0.0, 0.0, 0.0, 0.0)
    return user_food_list(state)


# ==========================================
# UNIT TESTS USING bakery assert_equal
# ==========================================

test_food = Food(
    name="Apple",
    grams=100.0,
    cals=52.0,
    protein=0.3,
    fats=0.2,
    fiber=2.4,
    carbs=13.8,
    category="Fruits"
)

test_state = State(
    all_foods=[test_food],
    search_query="",
    matching_foods=[],
    desired_foods=[],
    macro_totals=MacroTotals(0.0, 0.0, 0.0, 0.0, 0.0),
    error_message="",
    desired_grams="",
    selected_food=None,
    high_protein_filter=False
)

# 1. Test parse_food helper
mock_line = "Banana\t\t100\t89\t1.1\t0.3\t\t2.6\t22.8\tFruits"
parsed_result = parse_food(mock_line)
assert_equal(parsed_result.name, "Banana")
assert_equal(parsed_result.grams, 100.0)
assert_equal(parsed_result.cals, 89.0)

# 2. Test find_foods helper
assert_equal(find_foods([test_food], "appl"), [test_food])
assert_equal(find_foods([test_food], "Fruits"), [test_food])
assert_equal(find_foods([test_food], "pizza"), [])
assert_equal(find_foods([test_food], ""), [])

# 3. Test calculate_totals helper
selected_item = SelectedFood(food=test_food, desired_grams=200.0)
calculated_totals = calculate_totals([selected_item])
assert_equal(calculated_totals.total_calories, 104.0)
assert_equal(calculated_totals.total_protein, 0.6)
assert_equal(calculated_totals.total_carbs, 27.6)

# 4. Test index route page generation
assert_equal(
    index(test_state),
    Page(
        test_state,
        [
            Header("Macronutrient Tracker"),
            "",
            "Calories: 0.0",
            "Protein: 0.0g",
            "Carbs: 0.0g",
            "Fat: 0.0g",
            TextBox("search_query"),
            CheckBox(
                "high_protein_filter",
                label="High Protein Only (>= 10g)"
            ),
            Button("Search", "search"),
            Button("My Foods", "user_food_list")
        ]
    )
)

# 5. Test no_food_found_page route
assert_equal(
    no_food_found_page(test_state),
    Page(
        test_state,
        [
            Header("No results found"),
            "Try a different food or category",
            Button("Home", "index")
        ]
    )
)

# 6. Test view_food route
assert_equal(
    view_food(test_state, "Apple"),
    Page(
        test_state,
        [
            Header("Apple"),
            "",
            "Serving Size: 100.0 g",
            "Calories: 52.0",
            "Protein: 0.3 g",
            "Carbs: 13.8 g",
            "Fat: 0.2 g",
            "Fiber: 2.4 g",
            "Enter desired grams:",
            TextBox("desired_grams"),
            Button("Add Food", "add_food"),
            Button("Back", "index")
        ]
    )
)

# 7. Test search route
assert_equal(
    search(test_state, "Apple"),
    Page(
        test_state,
        [
            Header("Search Results"),
            Row(
                "Apple - Protein: 0.3g",
                Button(
                    "View Food",
                    "view_food",
                    arguments=[Argument("food_name", "Apple")]
                )
            ),
            Button("Back", "index")
        ]
    )
)

# 8. Test delete_food route function
state_with_food = State(
    all_foods=[test_food],
    search_query="",
    matching_foods=[],
    desired_foods=[SelectedFood(food=test_food, desired_grams=100.0)],
    macro_totals=MacroTotals(52.0, 0.3, 13.8, 0.2, 2.4),
    error_message="",
    desired_grams="",
    selected_food=test_food,
    high_protein_filter=False
)
expected_state_after_delete = State(
    all_foods=[test_food],
    search_query="",
    matching_foods=[],
    desired_foods=[],
    macro_totals=MacroTotals(0.0, 0.0, 0.0, 0.0, 0.0),
    error_message="",
    desired_grams="",
    selected_food=test_food,
    high_protein_filter=False
)
assert_equal(
    delete_food(state_with_food, "Apple"),
    user_food_list(expected_state_after_delete)
)


print("Program Loaded Successfully and All Unit Tests Passed!")

start_server(INITIAL_STATE)
