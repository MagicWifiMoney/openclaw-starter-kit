# Polymarket Trading API

**Authenticated access to Polymarket US for automated trading**

---

## 🔑 Credentials Stored

**Location:** `~/.env` and `~/clawd/.env`

```bash
POLYMARKET_API_KEY=541f31e2-e12e-48d3-8044-95a565787b5f
POLYMARKET_SECRET=9iuODoId/FC83E2uXw/QobpD7pjTqTnbX9f0YNZzzYOhr6Ti1oAK2sJWDfB23thvbiFqucSo3jNqEJ5UhK7GSg==
```

**Docs:** https://docs.polymarket.us/api/introduction

---

## 📊 API Capabilities

### **23 REST Endpoints + 2 WebSocket**

| Category | Endpoints | Capabilities |
|----------|-----------|--------------|
| **Markets** | 6 | Query markets, order books, BBO, settlement data |
| **Events** | 4 | Event data, search, filtering |
| **Series** | 2 | Series grouping (e.g., NFL 2025, NBA Playoffs) |
| **Sports** | 2 | Sports config, teams |
| **Orders** | 6 | Create, cancel, modify, preview, query |
| **Portfolio** | 2 | Positions, activities, P&L |
| **Account** | 1 | Balances, buying power |
| **WebSocket** | 2 | Real-time market data + private updates |

---

## 🚀 Key Features

### **Trading**
- ✅ Place limit & market orders
- ✅ Cancel orders (single or all)
- ✅ Modify existing orders
- ✅ Close positions
- ✅ Preview orders before submission
- ✅ Query open orders

### **Market Data**
- ✅ Full order book depth
- ✅ Best bid/offer (BBO) for efficient polling
- ✅ Market statistics
- ✅ Settlement prices
- ✅ Real-time WebSocket feeds (up to 10 markets)

### **Portfolio**
- ✅ View all positions
- ✅ Trading activities (trades, resolutions, balance changes)
- ✅ Account balances & buying power
- ✅ Real-time position updates via WebSocket

### **Search & Discovery**
- ✅ Full-text search across events/markets
- ✅ Filter by category (politics, crypto, sports)
- ✅ Browse series (grouped events)
- ✅ Sports teams data

---

## 📖 Documentation

**Full API Docs:** https://docs.polymarket.us/llms.txt (15KB reference)

**Key Pages:**
- Authentication: https://docs.polymarket.us/api/authentication
- Create Order: https://docs.polymarket.us/api-reference/orders/create-order
- Get Positions: https://docs.polymarket.us/api-reference/portfolio/get-user-positions
- Market Data: https://docs.polymarket.us/api-reference/markets/get-market-bbo
- WebSocket: https://docs.polymarket.us/api-reference/websocket/overview

**SDKs Available:**
- Python SDK: https://docs.polymarket.us/sdks/python/quickstart
- TypeScript SDK: https://docs.polymarket.us/sdks/typescript/quickstart

---

## 🛠️ Next Steps

### **Option A: Use Python SDK**
```bash
pip install polymarket-us
```

```python
from polymarket import PolymarketUS

client = PolymarketUS(
    api_key=os.environ['POLYMARKET_API_KEY'],
    secret=os.environ['POLYMARKET_SECRET']
)

# Get account balance
balance = client.get_account_balances()

# Search markets
markets = client.search("trump 2028")

# Get positions
positions = client.get_user_positions()

# Place order
order = client.create_order(
    market_slug="trump-wins-2028",
    side="yes",
    price=0.55,
    quantity=100
)
```

### **Option B: Use TypeScript SDK**
```bash
npm install @polymarket/us-sdk
```

```typescript
import { PolymarketUS } from '@polymarket/us-sdk';

const client = new PolymarketUS({
  apiKey: process.env.POLYMARKET_API_KEY,
  secret: process.env.POLYMARKET_SECRET
});

// Get balance
const balance = await client.getAccountBalances();

// Search
const markets = await client.search('bitcoin');

// Create order
const order = await client.createOrder({
  marketSlug: 'btc-100k-2026',
  side: 'yes',
  price: 0.42,
  quantity: 50
});
```

### **Option C: Direct REST API**
```bash
# Example: Get markets
curl -X GET "https://api.polymarket.us/v1/markets" \
  -H "X-API-Key: $POLYMARKET_API_KEY" \
  -H "X-API-Secret: $POLYMARKET_SECRET"
```

---

## 💡 Use Cases

**For Botti:**

1. **Market Monitoring**
   - Track odds on key events
   - Alert when spreads tighten
   - Find arbitrage opportunities

2. **Automated Trading**
   - Execute strategies based on news/data
   - Rebalance positions automatically
   - Close positions at target prices

3. **Portfolio Management**
   - Track P&L across all positions
   - Daily/weekly performance reports
   - Risk monitoring

4. **Research & Analysis**
   - Historical price data
   - Volume patterns
   - Correlation analysis

**Example Automation:**
```python
# Daily morning report
positions = client.get_user_positions()
balance = client.get_account_balances()

report = f"""
📊 Polymarket Portfolio Update

💰 Balance: ${balance['cash']}
📈 Positions: {len(positions)}
💵 Total Value: ${sum(p['current_value'] for p in positions)}

Top Positions:
{format_top_positions(positions)}
"""

send_to_slack(report)
```

---

## ⚠️ Important Notes

**Authentication:**
- Ed25519 API keys (generated in developer portal)
- Must use same auth method (Apple/Google/email) consistently
- Private key shown only once at generation

**Requirements:**
- Must have Polymarket US iOS app
- Account created + KYC verified
- Identity verification completed

**Trading Limits:**
- Check `/api-reference/trading/access-and-limits/trading-limits`
- CFTC-regulated exchange
- Compliance requirements apply

**Compliance:**
- Fully collateralized contracts
- Withdrawal rules enforced
- Account reviews may occur

---

## 🧪 Test Script

**Create:** `~/clawd/skills/polymarket/scripts/test-auth.py`

```python
#!/usr/bin/env python3
"""Test Polymarket US API authentication"""

import os
from polymarket import PolymarketUS

def main():
    # Load credentials
    api_key = os.environ.get('POLYMARKET_API_KEY')
    secret = os.environ.get('POLYMARKET_SECRET')
    
    if not api_key or not secret:
        print("❌ Missing credentials in environment")
        return
    
    # Initialize client
    client = PolymarketUS(api_key=api_key, secret=secret)
    
    try:
        # Test: Get account balance
        balance = client.get_account_balances()
        print(f"✅ Authentication successful")
        print(f"💰 Cash Balance: ${balance.get('cash', 0):.2f}")
        print(f"💵 Buying Power: ${balance.get('buying_power', 0):.2f}")
        
        # Test: Get positions
        positions = client.get_user_positions()
        print(f"📊 Open Positions: {len(positions)}")
        
        if positions:
            print("\nTop 3 Positions:")
            for pos in positions[:3]:
                print(f"  - {pos['market_slug']}: {pos['quantity']} @ ${pos['avg_price']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == '__main__':
    main()
```

---

## 🔗 Related Files

- **Read-only skill:** `~/clawd/skills/polymarket/SKILL.md` (old Gamma API)
- **Credentials:** `~/.env`, `~/clawd/.env`
- **Scripts:** `~/clawd/skills/polymarket/scripts/`

---

**Ready to trade on Polymarket programmatically** 🎯
