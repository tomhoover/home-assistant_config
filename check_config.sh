#!/bin/bash
docker exec -it hass python -m homeassistant --config /config --script check_config
BRANCH=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
RED=`tput setaf 1`
RESET=`tput sgr0`
echo ""
if [ "$BRANCH" != "master" ] ; then
    read -n 1 -s -r -p "${RED}YOU ARE NOT ON THE MASTER BRANCH.${RESET} Are you sure you wish to restart Home Assistant? [Y/n] " YN
else
    read -n 1 -s -r -p "Restart Home Assistant? [Y/n] " YN
fi
    [[ $YN == "y" || $YN == "Y" || $YN == "" ]] && echo "" && echo "  Restarting..." && docker restart hass && ssh pizw-0 sudo reboot ; tail -f home-assistant.log | ccze
    echo ""
