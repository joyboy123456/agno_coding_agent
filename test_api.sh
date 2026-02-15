#!/bin/bash
curl -s -X POST "https://fengyeai.chat/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-RibYzreuIKbqBtNJ3OYDNko54rSPFObThx6EUP1aLRxXSMVL" \
  -d '{"model":"kimi-k2.5","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
