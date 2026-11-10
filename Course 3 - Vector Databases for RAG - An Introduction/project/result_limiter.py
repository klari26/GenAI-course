from shared_functions import *

def test_result_limits():
    """Function to test how different result limits impacts search quality"""
    try:
        print("SIMILARITY SEARCH RESULT LIMITER")
        print("=" * 50)
        print("Loading food database...")

        global food_items
        food_items = load_food_data('./FoodDataSet.json')

        print(f"✅ Loaded {len(food_items)} food items successfully")

        collection = create_similarity_search_collection(
            "result_tester",
            {"description": "A collection for testing result limits"}
        )

        populate_similarity_collection(collection, food_items)

        while True:

            query = input("Write the query you want to test:").strip()

            # Handle empty input
            if not query:
                print("   Type an actual query!\n")
                continue
            
            # Handle exit commands
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using the result limits tester!")
                print("   Goodbye!")
                break
            
            print(f"Testing query: {query}\n")

            for limit in [1, 3, 5, 10]:
                print(f"Retrieving top {limit} result(s):")
                print("=" * 50)

                results = perform_similarity_search(collection, query, limit)

                if results:
                    for i, result in enumerate(results, 1):
                        percentage_score = result['similarity_score'] * 100
            
                        print(f"\n{i}. 🍽️  {result['food_name']}")
                        print(f"   📊 Match Score: {percentage_score:.1f}%")
                        print(f"   🏷️  Cuisine: {result['cuisine_type']}")
                        print(f"   🔥 Calories: {result['food_calories_per_serving']} per serving")
                        print(f"   📝 Description: {result['food_description']}")
                    
                    # Show quality analysis
                    scores = [r['similarity_score'] for r in results]
                    avg_score = sum(scores) / len(scores)
                    print(f"  📈 Average score: {avg_score:.3f}")
                    print(f"  🎯 Best score: {max(scores):.3f}")
                    if len(scores) > 1:
                        print(f"  📉 Worst score: {min(scores):.3f}")
                else:
                    print("  No results found!")
                
                print("=" * 45)
    except Exception as e:
        print(f"Error: {e}")

if __name__  == "__main__":
    test_result_limits()