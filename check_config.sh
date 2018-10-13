#!/bin/bash
docker exec -it home-assistant python -m homeassistant --config /config --script check_config
echo ""
read -n 1 -s -r -p "Restart Home Assistant? [Y/n] " YN
[[ $YN == "y" || $YN == "Y" || $YN == "" ]] && echo "" && echo "  Restarting..." && docker restart home-assistant
echo ""
