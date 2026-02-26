#!/usr/bin/env python3.11
"""Generate daily Polymarket portfolio report"""

import os
import sys
from datetime import datetime

def format_currency(value_dict):
    """Format currency value from API response"""
    if isinstance(value_dict, dict):
        return f"${value_dict.get('value', '0')}"
    return f"${value_dict}"

def format_percent(value):
    """Format percentage"""
    try:
        pct = float(value) * 100
        return f"{pct:+.2f}%"
    except:
        return "N/A"

def main():
    # Load credentials
    api_key = os.environ.get('POLYMARKET_API_KEY')
    secret = os.environ.get('POLYMARKET_SECRET')
    
    if not api_key or not secret:
        print("❌ Missing POLYMARKET_API_KEY or POLYMARKET_SECRET")
        return 1
    
    try:
        from polymarket_us import PolymarketUS
    except ImportError:
        print("❌ polymarket-us not installed")
        return 1
    
    try:
        client = PolymarketUS(key_id=api_key, secret_key=secret)
        
        # Get data
        balances = client.account.balances()
        positions_resp = client.portfolio.positions()
        activities_resp = client.portfolio.activities({"limit": 10})
        
        positions = positions_resp.get('positions', [])
        activities = activities_resp.get('activities', [])
        
        # Generate report
        report = []
        report.append("=" * 60)
        report.append("📊 POLYMARKET PORTFOLIO REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")
        
        # Account Balance
        cash = balances.get('cash', {}).get('value', '0')
        buying_power = balances.get('buyingPower', {}).get('value', '0')
        
        report.append("💰 ACCOUNT BALANCE")
        report.append(f"   Cash: ${cash}")
        report.append(f"   Buying Power: ${buying_power}")
        report.append("")
        
        # Positions
        if positions:
            total_value = sum(float(p.get('currentValue', {}).get('value', '0')) for p in positions)
            total_pnl = sum(float(p.get('pnl', {}).get('value', '0')) for p in positions)
            
            report.append(f"📈 POSITIONS ({len(positions)} total)")
            report.append(f"   Total Value: ${total_value:.2f}")
            report.append(f"   Total P&L: ${total_pnl:+.2f}")
            report.append("")
            
            # Top 10 positions
            sorted_positions = sorted(
                positions, 
                key=lambda p: abs(float(p.get('currentValue', {}).get('value', '0'))),
                reverse=True
            )
            
            report.append("Top Positions:")
            for i, pos in enumerate(sorted_positions[:10], 1):
                market_slug = pos.get('marketSlug', 'Unknown')
                quantity = pos.get('quantity', 0)
                avg_price = pos.get('avgPurchasePrice', {}).get('value', '0')
                current_value = pos.get('currentValue', {}).get('value', '0')
                pnl = pos.get('pnl', {}).get('value', '0')
                
                report.append(f"   {i}. {market_slug}")
                report.append(f"      Qty: {quantity} @ ${avg_price} = ${current_value}")
                report.append(f"      P&L: ${pnl}")
                report.append("")
        else:
            report.append("📈 POSITIONS")
            report.append("   No open positions")
            report.append("")
        
        # Recent Activity
        if activities:
            report.append(f"📝 RECENT ACTIVITY (Last {len(activities)})")
            report.append("")
            
            for activity in activities:
                activity_type = activity.get('type', 'UNKNOWN')
                timestamp = activity.get('createdAt', '')
                description = activity.get('description', 'No description')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%m/%d %H:%M')
                except:
                    time_str = timestamp
                
                report.append(f"   [{time_str}] {activity_type}")
                report.append(f"   {description}")
                
                # Show relevant details based on type
                if activity_type == 'ACTIVITY_TYPE_TRADE':
                    market_slug = activity.get('marketSlug', 'Unknown')
                    side = activity.get('side', 'UNKNOWN')
                    quantity = activity.get('quantity', 0)
                    price = activity.get('price', {}).get('value', '0')
                    report.append(f"   Market: {market_slug}")
                    report.append(f"   {side}: {quantity} @ ${price}")
                
                report.append("")
        else:
            report.append("📝 RECENT ACTIVITY")
            report.append("   No recent activity")
            report.append("")
        
        report.append("=" * 60)
        
        # Print report
        full_report = "\n".join(report)
        print(full_report)
        
        # Also save to file
        report_dir = os.path.expanduser("~/clawd/skills/polymarket/reports")
        os.makedirs(report_dir, exist_ok=True)
        
        filename = f"portfolio-{datetime.now().strftime('%Y-%m-%d')}.txt"
        filepath = os.path.join(report_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(full_report)
        
        print(f"\n💾 Saved to: {filepath}")
        
        client.close()
        return 0
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
