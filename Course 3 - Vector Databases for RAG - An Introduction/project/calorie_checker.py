from shared_functions import *

food_items=[]

def main():
    """Main function for interactive CLI Calorie Checker"""
    try:
        print("🍽️  Calorie CheckerSystem")
        print("=" * 50)
        print("Loading food database...")

        global food_items
        food_items = load_food_data('./FoodDataSet.json')

        print(f"✅ Loaded {len(food_items)} food items successfully")

        collection = create_similarity_search_collection(
            "calorie_checker",
            {"description": "A collection for checking calories"}
        )

        populate_similarity_collection(collection, food_items)

        calorie_checker_chatbot(collection)
    
    except Exception as e:
        print(f"❌ Error initializing system: {error}")

def calorie_checker_chatbot(collection):
    print("\n" + "="*50)
    print("🤖 CALORIE CHECK CHATBOT")
    print("="*50)
    print("Commands:")
    print("  • Type calorie budget")
    print("  • 'help' - Show available commands")
    print("  • 'quit' or 'exit' - Exit the system")
    print("  • Ctrl+C - Emergency exit")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n🔍 Submit your calorie budget: ").strip()
            
            # Handle empty input
            if not user_input:
                print("   Please enter a search term or 'help' for commands")
                continue
            
            # Handle exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using the Calorie Checking System!")
                print("   Goodbye!")
                break
            
            # Handle help command
            elif user_input.lower() in ['help', 'h']:
                show_help_menu()
            
            else:
                handle_food_search(collection, user_input)
                
        except KeyboardInterrupt:
            print("\n\n👋 System interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error processing request: {e}")

def show_help_menu():
    """Display help information for users"""
    print("\n📖 HELP MENU")
    print("-" * 30)
    print("Search Examples:")
    print("  • '500' - Find food items under the 500 calorie budget.")
    print("\nCommands:")
    print("  • 'help' - Show this help menu")
    print("  • 'quit' - Exit the system")

def handle_food_search(collection, user_input):
    """Perform calorie-filtered similarity search"""
    print("-" * 30)
    
    max_calories_input = user_input
    max_calories = None
    if max_calories_input.isdigit():
        max_calories = int(max_calories_input)
        if max_calories < 0:
            max_calories = int(input("Please enter a positive number:"))

    query = input("Enter search query: ").strip()
    
    if not query:
        print("❌ Please enter a search term")
        return
    
    print(f"\n🔍 Searching for '{query}'" + 
          (f" with max {max_calories} calories..." if max_calories else "..."))
    
    # Search for foods within budget
    budget_results = perform_filtered_similarity_search(
        collection, query, max_calories=max_calories, n_results=5
    )
    # Also get regular results to show what's over budget
    all_results = perform_similarity_search(collection, query, 5)
    print(f"\n📋 Results for '{query}':")
    if budget_results:
        print(f"✅ FITS YOUR BUDGET ({max_calories} cal limit):")
        for i, result in enumerate(budget_results, 1):
            calories = result['food_calories_per_serving']
            remaining = max_calories - calories
            print(f"  {i}. {result['food_name']}")
            print(f"     Calories: {calories} (🟢 {remaining} cal remaining)")
            print(f"     Cuisine: {result['cuisine_type']}")
    else:
        print(f"❌ No foods found within your {max_calories} calorie budget!")
    # Show over-budget options
    over_budget = []
    for result in all_results:
        if result['food_calories_per_serving'] > max_calories:
            over_budget.append(result)
    if over_budget:
        print(f"\n🚫 OVER BUDGET (but similar to your search):")
        for i, result in enumerate(over_budget[:3], 1):
            calories = result['food_calories_per_serving']
            excess = calories - max_calories
            print(f"  {i}. {result['food_name']}")
            print(f"     Calories: {calories} (🔴 {excess} cal over budget)")
    # Show budget summary
    if budget_results:
        avg_calories = sum(r['food_calories_per_serving'] for r in budget_results) / len(budget_results)
        print(f"\n📊 Budget-friendly options average: {avg_calories:.0f} calories")

if __name__ == "__main__":
    main()