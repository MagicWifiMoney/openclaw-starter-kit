#!/usr/bin/env python3.11
"""Search and monitor Polymarket markets"""

import os
import sys

def format_price(value_dict):
    """Format price from API response"""
    if isinstance(value_dict, dict):
        value = value_dict.get('value', '0')
    else:
        value = value_dict
    
    try:
        # Convert to probability %
        prob = float(value) * 100
        return f"{prob:.1f}%"
    except:
        return "N/A"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3.11 market-search.py <query>")
        print()
        print("Examples:")
        print("  python3.11 market-search.py trump")
        print("  python3.11 market-search.py bitcoin")
        print("  python3.11 market-search.py \"super bowl\"")
        return 1
    
    query = " ".join(sys.argv[1:])
    
    # API key not required for public search
    try:
        from polymarket_us import PolymarketUS
    except ImportError:
        print("❌ polymarket-us not installed")
        return 1
    
    try:
        client = PolymarketUS()  # No auth needed for search
        
        print(f"🔍 Searching for: \"{query}\"")
        print()
        
        # Search
        results = client.search.query({"query": query})
        events = results.get('events', [])
        
        if not events:
            print("No results found.")
            return 0
        
        print(f"Found {len(events)} event(s):")
        print()
        
        for i, event in enumerate(events[:10], 1):  # Top 10
            title = event.get('title', 'Unknown Event')
            markets = event.get('markets', [])
            
            print(f"{i}. {title}")
            
            if markets:
                for market in markets:
                    slug = market.get('slug', 'unknown')
                    description = market.get('question', slug.replace('-', ' ').title())
                    
                    # Get pricing
                    bbo = market.get('bbo', {})
                    bid = bbo.get('bid', {})
                    ask = bbo.get('ask', {})
                    
                    bid_price = format_price(bid)
                    ask_price = format_price(ask)
                    
                    # Calculate mid price
                    try:
                        bid_val = float(bid.get('value', '0'))
                        ask_val = float(ask.get('value', '0'))
                        if bid_val > 0 and ask_val > 0:
                            mid = (bid_val + ask_val) / 2 * 100
                            mid_str = f"{mid:.1f}%"
                        else:
                            mid_str = "N/A"
                    except:
                        mid_str = "N/A"
                    
                    # Volume
                    volume = market.get('volume24h', {})
                    volume_val = volume.get('value', '0') if isinstance(volume, dict) else volume
                    
                    print(f"   📊 {description}")
                    print(f"      Slug: {slug}")
                    print(f"      Odds: {mid_str} (bid {bid_price} / ask {ask_price})")
                    print(f"      24h Volume: ${volume_val}")
                    print()
            else:
                print("   No active markets")
                print()
        
        if len(events) > 10:
            print(f"... and {len(events) - 10} more results")
        
        client.close()
        return 0
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
