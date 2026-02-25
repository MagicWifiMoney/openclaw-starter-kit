#!/bin/bash
# HelpScout Reply Wrapper
# Usage: helpscout-reply.sh <conversation_id> <message_text>

export HELPSCOUT_APP_ID="94alE5zhvHelEYkrTCADilMgbLCHwFau"
export HELPSCOUT_APP_SECRET="lZrAH5H0ZiLy2zbcy9M71JLCSBTRfOVH"
export HELPSCOUT_MAILBOX_ID="312775"

node /home/ec2-user/clawd/skills/helpscout/scripts/helpscout.js reply "$@"
