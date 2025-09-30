"""
LLM integration module for coupon scoring.
Supports Anthropic, Groq, and Ollama.
"""

import requests
import json
import config

def generate_completion(prompt: str) -> str:
    """
    Generate a completion using the configured LLM provider.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        String response from the LLM
    """
    provider = config.LLM_PROVIDER.lower()
    
    if provider == "anthropic":
        return generate_anthropic(prompt)
    elif provider == "groq":
        return generate_groq(prompt)
    elif provider == "ollama":
        return generate_ollama(prompt)
    else:
        print(f"Unknown provider: {provider}, defaulting to anthropic")
        return generate_anthropic(prompt)

def generate_anthropic(prompt: str) -> str:
    """Generate completion using Anthropic Claude API."""
    headers = {
        "x-api-key": config.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 10,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(config.ANTHROPIC_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"Anthropic API error: {e}")
        return "0.5"

def generate_groq(prompt: str) -> str:
    """Generate completion using Groq API."""
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(config.GROQ_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        return "0.5"

def generate_ollama(prompt: str) -> str:
    """Generate completion using Ollama local API."""
    payload = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 10,
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(config.OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "0.5").strip()
    except Exception as e:
        print(f"Ollama API error: {e}")
        return "0.5"

def score_relevance(context: str, coupon_text: str) -> float:
    """
    Score the relevance of a coupon to given context.
    
    Args:
        context: User conversation context
        coupon_text: Coupon description
        
    Returns:
        Float score between 0 and 1
    """
    prompt = f"""Rate the relevance of this coupon to the user's context on a scale from 0 to 1.
Return only a number between 0 and 1.

User Context: {context}
Coupon: {coupon_text}

Score:"""
    
    try:
        response = generate_completion(prompt)
        score = float(response.strip())
        return max(0.0, min(1.0, score))
    except ValueError:
        return 0.5