"""
Test script to verify dashboard API response format.
Run this to check if the backend returns the correct structure.
"""

import json
from datetime import datetime, timedelta
from app.services import AnalyticsService
from app.db import AthenaClient, SupabaseClient

def test_dashboard_summary():
    """Test the dashboard summary function."""
    print("=" * 80)
    print("TESTING DASHBOARD SUMMARY API")
    print("=" * 80)
    
    try:
        # Initialize services
        athena = AthenaClient()
        supabase = SupabaseClient()
        analytics = AnalyticsService(athena, supabase)
        
        # Use today's date
        test_date = datetime.now().date()
        
        print(f"\nTesting with date: {test_date}")
        print("-" * 80)
        
        # Call the service
        result = analytics.get_dashboard_summary(test_date)
        
        print("\nResponse Structure:")
        print(json.dumps(result, indent=2, default=str))
        
        # Validate structure
        print("\n" + "=" * 80)
        print("VALIDATION CHECK")
        print("=" * 80)
        
        required_fields = {
            "date": str,
            "market": dict,
            "top_gainers": list,
            "top_losers": list,
            "sentiment": dict,
            "macro": dict,
            "latest_update": (str, type(None))
        }
        
        market_fields = {
            "total_stocks": int,
            "market_change_pct": (int, float),
            "advancing": int,
            "declining": int,
            "unchanged": int,
            "total_volume": int
        }
        
        sentiment_fields = {
            "avg_score": (int, float),
            "positive_pct": (int, float),
            "total_articles": int
        }
        
        macro_fields = {
            "cpi": (int, float),
            "usd_vnd": (int, float)
        }
        
        # Check top-level fields
        print("\n✓ Checking top-level fields...")
        for field, expected_type in required_fields.items():
            if field in result:
                actual_type = type(result[field])
                if isinstance(expected_type, tuple):
                    if actual_type in expected_type:
                        print(f"  ✓ {field}: {actual_type.__name__}")
                    else:
                        print(f"  ✗ {field}: Expected {expected_type}, got {actual_type}")
                else:
                    if actual_type == expected_type:
                        print(f"  ✓ {field}: {actual_type.__name__}")
                    else:
                        print(f"  ✗ {field}: Expected {expected_type.__name__}, got {actual_type.__name__}")
            else:
                print(f"  ✗ {field}: MISSING")
        
        # Check market fields
        print("\n✓ Checking market object fields...")
        if "market" in result:
            market = result["market"]
            for field, expected_type in market_fields.items():
                if field in market:
                    actual_type = type(market[field])
                    if isinstance(expected_type, tuple):
                        if actual_type in expected_type:
                            print(f"  ✓ market.{field}: {actual_type.__name__} = {market[field]}")
                        else:
                            print(f"  ✗ market.{field}: Expected {expected_type}, got {actual_type}")
                    else:
                        if actual_type == expected_type:
                            print(f"  ✓ market.{field}: {actual_type.__name__} = {market[field]}")
                        else:
                            print(f"  ✗ market.{field}: Expected {expected_type.__name__}, got {actual_type.__name__}")
                else:
                    print(f"  ✗ market.{field}: MISSING")
        
        # Check sentiment fields
        print("\n✓ Checking sentiment object fields...")
        if "sentiment" in result:
            sentiment = result["sentiment"]
            for field, expected_type in sentiment_fields.items():
                if field in sentiment:
                    actual_type = type(sentiment[field])
                    if isinstance(expected_type, tuple):
                        if actual_type in expected_type:
                            print(f"  ✓ sentiment.{field}: {actual_type.__name__} = {sentiment[field]}")
                        else:
                            print(f"  ✗ sentiment.{field}: Expected {expected_type}, got {actual_type}")
                    else:
                        if actual_type == expected_type:
                            print(f"  ✓ sentiment.{field}: {actual_type.__name__} = {sentiment[field]}")
                        else:
                            print(f"  ✗ sentiment.{field}: Expected {expected_type.__name__}, got {actual_type.__name__}")
                else:
                    print(f"  ✗ sentiment.{field}: MISSING")
        
        # Check macro fields
        print("\n✓ Checking macro object fields...")
        if "macro" in result:
            macro = result["macro"]
            for field, expected_type in macro_fields.items():
                if field in macro:
                    actual_type = type(macro[field])
                    if isinstance(expected_type, tuple):
                        if actual_type in expected_type:
                            print(f"  ✓ macro.{field}: {actual_type.__name__} = {macro[field]}")
                        else:
                            print(f"  ✗ macro.{field}: Expected {expected_type}, got {actual_type}")
                    else:
                        if actual_type == expected_type:
                            print(f"  ✓ macro.{field}: {actual_type.__name__} = {macro[field]}")
                        else:
                            print(f"  ✗ macro.{field}: Expected {expected_type.__name__}, got {actual_type.__name__}")
                else:
                    print(f"  ✗ macro.{field}: MISSING")
        
        print("\n" + "=" * 80)
        print("✓ VALIDATION COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_summary()
