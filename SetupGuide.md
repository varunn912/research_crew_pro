# 🚀 Complete Setup Guide

## Quick Start (5 Minutes)

### Option A: Groq (Recommended) ⭐

**Why Groq?**
- Free & fast
- No rate limits (30 req/min)
- Best for most users

**Setup:**
```bash
1. Visit: https://console.groq.com/
2. Sign up (free)
3. Get API key
4. Add to .env:
   GROQ_API_KEY=gsk_your_key_here
   LLM_PROVIDER=groq
5. Run: streamlit run app.py
```

### Option B: Ollama (Local - 100% Free)

**Why Ollama?**
- Completely free
- Privacy (runs locally)
- No internet needed

**Setup:**
```bash
# Install Ollama
# Windows: Download from ollama.ai
# Mac: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3

# Update .env
LLM_PROVIDER=ollama

# Run
streamlit run app.py
```

### Option C: OpenAI (Requires Payment)

**Only if you have a paid OpenAI account:**
```bash
# Add to .env
OPENAI_API_KEY=sk-your_key_here
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# Note: Free tier has 3 req/min limit
```

---

## 🔧 Troubleshooting

### Error: Rate Limit Exceeded

**Solution 1: Use Groq (Best)**
```bash
python setup_llm.py
# Choose option 1 (Groq)
```

**Solution 2: Use Ollama (Local)**
```bash
# Install Ollama
ollama pull llama3

# Update .env
LLM_PROVIDER=ollama
```

**Solution 3: Wait & Retry**
```bash
# OpenAI free tier resets after 1 minute
# Just wait 60 seconds and try again
```

### Error: No LLM Providers Available
```bash
# Run setup wizard
python setup_llm.py

# Or manually set up Groq:
# 1. Get key from console.groq.com
# 2. Add to .env: GROQ_API_KEY=gsk_...
```

### Error: Import Failed
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Test installation
python test_providers.py
```

---

## 🎯 API Key Priority

The system tries providers in this order:

1. **LLM_PROVIDER** (if set in .env)
2. **Groq** (if GROQ_API_KEY exists)
3. **Anthropic** (if ANTHROPIC_API_KEY exists)
4. **Ollama** (if running locally)
5. **OpenAI** (if OPENAI_API_KEY exists)

---

## 💰 Cost Comparison

| Provider | Cost | Rate Limit | Speed | Quality |
|----------|------|------------|-------|---------|
| Groq | FREE | 30/min | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| Ollama | FREE | Unlimited | ⚡⚡ | ⭐⭐⭐ |
| OpenAI | $0.0001/1K | 3/min (free) | ⚡ | ⭐⭐⭐⭐⭐ |
| Anthropic | $0.00025/1K | 50/min | ⚡⚡ | ⭐⭐⭐⭐⭐ |

---

## 🔄 Switching Providers

Just update `.env`:
```bash
# Switch to Groq
LLM_PROVIDER=groq

# Switch to Ollama
LLM_PROVIDER=ollama

# Switch to OpenAI
LLM_PROVIDER=openai

# Auto-select (tries all)
LLM_PROVIDER=auto
```

Then restart the app.

---

## ✅ Verification

Test everything works:
```bash
# Run tests
python test_providers.py

# Should show:
# ✅ Active Providers: X
# ✅ LLM initialized successfully!
# ✅ All tests passed!
```

---

## 🆘 Still Having Issues?

1. **Check API keys** in `.env`
2. **Run setup wizard**: `python setup_llm.py`
3. **Test providers**: `python test_providers.py`
4. **Check logs** in terminal output
5. **Try Ollama** (works offline, no API keys needed)

---

## 📞 Get Help

- Check error messages carefully
- Run diagnostic: `python test_providers.py`
- Most issues = missing/invalid API keys
- **Quick fix: Use Groq or Ollama**