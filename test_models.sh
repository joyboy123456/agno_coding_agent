#!/bin/bash
curl -s "https://fengyeai.chat/v1/models" \
  -H "Authorization: Bearer sk-RibYzreuIKbqBtNJ3OYDNko54rSPFObThx6EUP1aLRxXSMVL" | python3 -m json.tool
