# Polymarket SDK - Quick Start

**Authenticated trading access to Polymarket US**

---

## ✅ SDK Installed

**Package:** `polymarket-us` (v0.1.2)  
**Python:** 3.11+ required  
**Status:** Installed and tested

---

## 🔑 Authentication

**Credentials stored in:**
- `~/.env`
- `~/clawd/.env`

**Environment variables:**
```bash
POLYMARKET_API_KEY=541f31e2-e12e-48d3-8044-95a565787b5f
POLYMARKET_SECRET=9iuODoId/FC83E2uXw/QobpD7pjTqTnbX9f0YNZzzYOhr6Ti1oAK2sJWDfB23thvbiFqucSo3jNqEJ5UhK7GSg==
```

---

## 🚀 Quick Commands

### Test Authentication
```bash
python3.11 ~/clawd/skills/polymarket/scripts/test-auth.py
```

**Output:**
```
✅ Authentication successful!
💰 Account Balances:
   Cash: $0
   Buying Power: $0
📊 Open Positions: 0
```

### List Active Markets
```bash
python3.11 ~/clawd/skills/polymarket/scripts/list-markets.py
```

### Search Markets
```bash
python3.11 ~/clawd/skills/polymarket/scripts/market-search.py "trump"
python3.11 ~/clawd/skills/polymarket/scripts/market-search.py "bitcoin"
```

### Portfolio Report
```bash
python3.11 ~/clawd/skills/polymarket/scripts/portfolio-report.py
```

**Saves to:** `~/clawd/skills/polymarket/reports/portfolio-YYYY-MM-DD.txt`

---

## 📖 Python API Usage

### Basic Setup

```python
#!/usr/bin/env python3.11
import os
from polymarket_us import PolymarketUS

# Initialize client
client = PolymarketUS(
    key_id=os.environ['POLYMARKET_API_KEY'],
    secret_key=os.environ['POLYMARKET_SECRET']
)
```

### Get Account Balance

```python
balances = client.account.balances()
cash = balances['cash']['value']
buying_power = balances['buyingPower']['value']

print(f"Cash: ${cash}")
print(f"Buying Power: ${buying_power}")
```

### Search Markets

```python
# Public endpoint (no auth needed)
client = PolymarketUS()
results = client.search.query({"query": "trump 2028"})

for event in results['events']:
    print(event['title'])
    for market in event.get('markets', []):
        print(f"  - {market['slug']}")
        print(f"    Odds: {market['bbo']['bid']['value']}")
```

### List Markets

```python
markets = client.markets.list({"limit": 20, "active": True})

for market in markets['markets']:
    print(market['question'])
    print(f"Slug: {market['slug']}")
```

### Get Market Details

```python
# By slug
market = client.markets.retrieve_by_slug("btc-100k-2025")

# Get order book
book = client.markets.book("btc-100k-2025")

# Get best bid/offer (lighter weight)
bbo = client.markets.bbo("btc-100k-2025")
print(f"Bid: {bbo['bid']['value']}")
print(f"Ask: {bbo['ask']['value']}")
```

### Place an Order

```python
order = client.orders.create({
    "marketSlug": "btc-100k-2025",
    "intent": "ORDER_INTENT_BUY_LONG",
    "type": "ORDER_TYPE_LIMIT",
    "price": {"value": "0.55", "currency": "USD"},
    "quantity": 100,
    "tif": "TIME_IN_FORCE_GOOD_TILL_CANCEL"
})

print(f"Order ID: {order['id']}")
```

### Get Positions

```python
positions = client.portfolio.positions()

for pos in positions['positions']:
    print(f"{pos['marketSlug']}: {pos['quantity']} @ ${pos['avgPurchasePrice']['value']}")
    print(f"  Current Value: ${pos['currentValue']['value']}")
    print(f"  P&L: ${pos['pnl']['value']}")
```

### Cancel Orders

```python
# Cancel specific order
client.orders.cancel(order_id, {"marketSlug": "btc-100k-2025"})

# Cancel all orders
client.orders.cancel_all()

# Cancel all orders for specific market
client.orders.cancel_all({"marketSlugs": ["btc-100k-2025"]})
```

### Close Position

```python
# Sell all shares in a market
client.orders.close_position({
    "marketSlug": "btc-100k-2025"
})
```

---

## 📊 Available Scripts

| Script | Purpose | Auth Required |
|--------|---------|---------------|
| `test-auth.py` | Test authentication & show balances | ✅ Yes |
| `list-markets.py` | Show active markets | ❌ No |
| `market-search.py` | Search markets by keyword | ❌ No |
| `portfolio-report.py` | Daily portfolio summary | ✅ Yes |

---

## 🔗 API Endpoints

### Public (No Auth)
- `client.events.list()` - List events
- `client.markets.list()` - List markets
- `client.markets.bbo(slug)` - Get best bid/offer
- `client.search.query()` - Search events/markets
- `client.series.list()` - List series
- `client.sports.list()` - List sports

### Authenticated
- `client.account.balances()` - Account balance
- `client.orders.create()` - Place order
- `client.orders.list()` - Get open orders
- `client.orders.cancel()` - Cancel order
- `client.orders.cancel_all()` - Cancel all
- `client.portfolio.positions()` - Get positions
- `client.portfolio.activities()` - Get activity history

---

## 💡 Use Cases

### Daily Morning Report
Run `portfolio-report.py` via cron at 8am:
```bash
0 8 * * * cd ~/clawd/skills/polymarket && python3.11 scripts/portfolio-report.py | mail -s "Polymarket Report" jake.giebel@gmail.com
```

### Market Alert Bot
Monitor specific markets and alert on price moves:
```python
while True:
    bbo = client.markets.bbo("trump-wins-2028")
    mid_price = (float(bbo['bid']['value']) + float(bbo['ask']['value'])) / 2
    
    if mid_price > 0.60:
        send_alert(f"Trump 2028 odds hit {mid_price*100}%!")
    
    time.sleep(300)  # Check every 5 min
```

### Auto-Close Positions at Target
```python
positions = client.portfolio.positions()

for pos in positions['positions']:
    current_value = float(pos['currentValue']['value'])
    pnl = float(pos['pnl']['value'])
    
    # Take profit at +20%
    if pnl / current_value > 0.20:
        client.orders.close_position({
            "marketSlug": pos['marketSlug']
        })
        print(f"Closed {pos['marketSlug']} at +{pnl:.2f}")
```

---

## 📚 Documentation

**Full API Docs:** https://docs.polymarket.us/api/introduction  
**SDK GitHub:** https://github.com/Polymarket/polymarket-us-python  
**Python SDK Docs:** https://docs.polymarket.us/sdks/python/quickstart

---

## ⚠️ Important Notes

**Account Requirements:**
- Polymarket US iOS app installed
- Account created + KYC verified
- API keys generated at https://polymarket.us/developer

**Rate Limits:**
- Check API docs for current limits
- SDK handles retries automatically

**Trading Hours:**
- Markets trade 24/7
- Some markets may pause during resolution

**Compliance:**
- CFTC-regulated exchange
- Must be US resident
- Withdrawal rules apply

---

## 🧪 Testing

**Run all tests:**
```bash
cd ~/clawd/skills/polymarket

# Test auth
python3.11 scripts/test-auth.py

# List markets
python3.11 scripts/list-markets.py | head -30

# Portfolio report
python3.11 scripts/portfolio-report.py
```

---

**Ready to trade! 🎯**
