#!/usr/bin/env python3.11
"""List active Polymarket markets"""

import os
import sys

def format_price(value_dict):
    """Format price from API response"""
    if isinstance(value_dict, dict):
        value = value_dict.get('value', '0')
    else:
        value = value_dict
    
    try:
        prob = float(value) * 100
        return f"{prob:.1f}%"
    except:
        return "N/A"

def main():
    try:
        from polymarket_us import PolymarketUS
    except ImportError:
        print("❌ polymarket-us not installed")
        return 1
    
    try:
        client = PolymarketUS()
        
        print("📊 Fetching active markets...")
        print()
        
        # Get markets
        markets_resp = client.markets.list({"limit": 20, "active": True})
        markets = markets_resp.get('markets', [])
        
        if not markets:
            print("No active markets found.")
            
            # Try without active filter
            print("\nTrying all markets...")
            markets_resp = client.markets.list({"limit": 20})
            markets = markets_resp.get('markets', [])
            
            if not markets:
                print("No markets found at all.")
                return 0
        
        print(f"Found {len(markets)} market(s):")
        print()
        
        for i, market in enumerate(markets, 1):
            slug = market.get('slug', 'unknown')
            question = market.get('question', slug.replace('-', ' ').title())
            
            # Get pricing
            bbo = market.get('bbo', {})
            bid = bbo.get('bid', {})
            ask = bbo.get('ask', {})
            
            bid_price = format_price(bid)
            ask_price = format_price(ask)
            
            # Calculate mid
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
            
            print(f"{i}. {question}")
            print(f"   Slug: {slug}")
            print(f"   Odds: {mid_str} (bid {bid_price} / ask {ask_price})")
            print()
        
        client.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
