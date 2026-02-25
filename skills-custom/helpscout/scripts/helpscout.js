#!/usr/bin/env node
const https = require('https');

// Read env vars
const APP_ID = process.env.HELPSCOUT_APP_ID;
const APP_SECRET = process.env.HELPSCOUT_APP_SECRET;
const MAILBOX_ID = process.env.HELPSCOUT_MAILBOX_ID;

let cachedToken = null;
let tokenExpiry = null;

// Rate limiter - HelpScout allows 200 req/min, we use 100 to be safe
class RateLimiter {
  constructor(maxRequests = 100, windowMs = 60000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = [];
    this.minDelayMs = 350; // Minimum delay between requests
  }

  async waitIfNeeded() {
    const now = Date.now();
    
    // Remove requests outside the current window
    this.requests = this.requests.filter(time => now - time < this.windowMs);
    
    // If we're at the limit, wait until the oldest request expires
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = this.windowMs - (now - oldestRequest) + 100; // +100ms buffer
      console.error(`Rate limit approaching, waiting ${Math.ceil(waitTime/1000)}s...`);
      await this.sleep(waitTime);
      return this.waitIfNeeded(); // Recursive check
    }
    
    // Add minimum delay between all requests
    if (this.requests.length > 0) {
      const lastRequest = Math.max(...this.requests);
      const timeSinceLastRequest = now - lastRequest;
      if (timeSinceLastRequest < this.minDelayMs) {
        await this.sleep(this.minDelayMs - timeSinceLastRequest);
      }
    }
    
    this.requests.push(Date.now());
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async handleRateLimitError(retryAfterSeconds) {
    const waitMs = (retryAfterSeconds || 60) * 1000;
    console.error(`Rate limited! Waiting ${retryAfterSeconds || 60}s before retry...`);
    await this.sleep(waitMs);
  }
}

const rateLimiter = new RateLimiter();

function httpsRequest(options, data = null) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        // Handle rate limiting
        if (res.statusCode === 429) {
          const retryAfter = res.headers['retry-after'];
          resolve({ 
            _rateLimited: true, 
            retryAfter: parseInt(retryAfter) || 60,
            statusCode: 429
          });
          return;
        }
        
        try {
          resolve({ ...JSON.parse(body), statusCode: res.statusCode });
        } catch (e) {
          resolve({ body, statusCode: res.statusCode });
        }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function getAccessToken() {
  // Always get a fresh token for now (caching can be added later)
  const data = `grant_type=client_credentials&client_id=${APP_ID}&client_secret=${APP_SECRET}`;
  const result = await httpsRequest({
    hostname: 'api.helpscout.net',
    path: '/v2/oauth2/token',
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Content-Length': data.length
    }
  }, data);

  if (!result.access_token) {
    throw new Error('Failed to get access token: ' + JSON.stringify(result));
  }

  return result.access_token;
}

async function apiRequest(path, method = 'GET', body = null, retryCount = 0) {
  // Wait for rate limiter before making request
  await rateLimiter.waitIfNeeded();
  
  const token = await getAccessToken();
  const options = {
    hostname: 'api.helpscout.net',
    path: `/v2${path}`,
    method,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  };

  let result;
  if (body) {
    const data = JSON.stringify(body);
    options.headers['Content-Length'] = data.length;
    result = await httpsRequest(options, data);
  } else {
    result = await httpsRequest(options);
  }
  
  // Handle rate limiting with exponential backoff
  if (result._rateLimited) {
    if (retryCount >= 3) {
      throw new Error('Max retries exceeded after rate limiting');
    }
    await rateLimiter.handleRateLimitError(result.retryAfter);
    return apiRequest(path, method, body, retryCount + 1);
  }
  
  return result;
}

async function listConversations(status = 'active', limit = 25) {
  const result = await apiRequest(`/conversations?mailbox=${MAILBOX_ID}&status=${status}&page=1&pageSize=${limit}`);
  return result._embedded?.conversations || [];
}

async function getConversation(id) {
  return await apiRequest(`/conversations/${id}`);
}

async function getThreads(conversationId) {
  const result = await apiRequest(`/conversations/${conversationId}/threads`);
  return result._embedded?.threads || [];
}

async function replyToConversation(conversationId, text, type = 'reply') {
  // Get conversation details to get customer ID
  const convo = await apiRequest(`/conversations/${conversationId}`);
  
  const customerId = convo.primaryCustomer?.id;
  
  if (!customerId) {
    throw new Error(`Could not find customer ID in conversation ${conversationId}`);
  }
  
  // User ID for admin@fifti-fifti.net
  const userId = 759476;
  
  return await apiRequest(`/conversations/${conversationId}/reply`, 'POST', {
    text,
    user: userId,
    customer: {
      id: customerId
    },
    status: 'active'
  });
}

async function updateConversation(conversationId, updates) {
  return await apiRequest(`/conversations/${conversationId}`, 'PATCH', updates);
}

// CLI
const [,, command, ...args] = process.argv;

(async () => {
  try {
    switch (command) {
      case 'list':
        const status = args[0] || 'active';
        const convos = await listConversations(status, 50);
        console.log(JSON.stringify(convos, null, 2));
        break;

      case 'get':
        const id = args[0];
        if (!id) throw new Error('Usage: get <conversation_id>');
        const convo = await getConversation(id);
        const threads = await getThreads(id);
        console.log(JSON.stringify({ conversation: convo, threads }, null, 2));
        break;

      case 'reply':
        const [convId, ...textParts] = args;
        if (!convId || textParts.length === 0) {
          throw new Error('Usage: reply <conversation_id> <text>');
        }
        const replyText = textParts.join(' ');
        await replyToConversation(convId, replyText);
        console.log('Reply sent');
        break;

      case 'close':
        const closeId = args[0];
        if (!closeId) throw new Error('Usage: close <conversation_id>');
        await updateConversation(closeId, { status: 'closed' });
        console.log('Conversation closed');
        break;

      default:
        console.log(`
HelpScout CLI

Commands:
  list [status]              - List conversations (default: active)
  get <id>                   - Get conversation details + threads
  reply <id> <text>          - Reply to conversation
  close <id>                 - Close conversation

Status options: active, pending, closed, spam
        `);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
})();
