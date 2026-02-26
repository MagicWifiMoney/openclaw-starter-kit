#!/usr/bin/env python3.11
"""Test Polymarket US API authentication"""

import os
import sys

def main():
    # Load credentials
    api_key = os.environ.get('POLYMARKET_API_KEY')
    secret = os.environ.get('POLYMARKET_SECRET')
    
    if not api_key or not secret:
        print("❌ Missing credentials in environment")
        print("   Set POLYMARKET_API_KEY and POLYMARKET_SECRET")
        return 1
    
    try:
        from polymarket_us import PolymarketUS
    except ImportError:
        print("❌ polymarket-us not installed")
        print("   Run: python3.11 -m pip install git+https://github.com/Polymarket/polymarket-us-python.git")
        return 1
    
    # Initialize client
    try:
        client = PolymarketUS(
            key_id=api_key,
            secret_key=secret
        )
        
        print("🔑 Authenticating with Polymarket US...")
        
        # Test: Get account balance
        balances = client.account.balances()
        print(f"✅ Authentication successful!")
        print()
        
        # Display balances
        cash = balances.get('cash', {}).get('value', '0')
        buying_power = balances.get('buyingPower', {}).get('value', '0')
        
        print(f"💰 Account Balances:")
        print(f"   Cash: ${cash}")
        print(f"   Buying Power: ${buying_power}")
        print()
        
        # Test: Get positions
        try:
            positions = client.portfolio.positions()
            position_list = positions.get('positions', [])
            print(f"📊 Open Positions: {len(position_list)}")
            
            if position_list:
                print()
                print("Top 5 Positions:")
                for i, pos in enumerate(position_list[:5], 1):
                    market_slug = pos.get('marketSlug', 'Unknown')
                    quantity = pos.get('quantity', 0)
                    avg_price = pos.get('avgPurchasePrice', {}).get('value', '0')
                    current_value = pos.get('currentValue', {}).get('value', '0')
                    
                    print(f"  {i}. {market_slug}")
                    print(f"     Quantity: {quantity} @ ${avg_price}")
                    print(f"     Value: ${current_value}")
                    print()
        except Exception as e:
            print(f"⚠️  Could not fetch positions: {e}")
        
        # Test: Search markets
        try:
            search_results = client.search.query({"query": "trump"})
            events = search_results.get('events', [])
            print(f"🔍 Search Test (\"trump\"): {len(events)} results")
            
            if events:
                print()
                print("Top 3 Results:")
                for i, event in enumerate(events[:3], 1):
                    title = event.get('title', 'Unknown')
                    markets = event.get('markets', [])
                    print(f"  {i}. {title}")
                    print(f"     Markets: {len(markets)}")
                    if markets:
                        for market in markets[:2]:
                            slug = market.get('slug', 'unknown')
                            bbo = market.get('bbo', {})
                            bid = bbo.get('bid', {}).get('value', 'N/A')
                            ask = bbo.get('ask', {}).get('value', 'N/A')
                            print(f"       - {slug}: bid ${bid} / ask ${ask}")
                    print()
        except Exception as e:
            print(f"⚠️  Could not search markets: {e}")
        
        client.close()
        return 0
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
