"""Constants for the pi_hole intergration."""
from datetime import timedelta

DOMAIN = "pi_hole"

CONF_LOCATION = "location"

DEFAULT_HOST = "pi.hole"
DEFAULT_LOCATION = "admin"
DEFAULT_METHOD = "GET"
DEFAULT_NAME = "Pi-Hole"
DEFAULT_SSL = False
DEFAULT_VERIFY_SSL = True

SERVICE_DISABLE = "disable"
SERVICE_ENABLE = "enable"
SERVICE_DISABLE_ATTR_DURATION = "duration"

ATTR_BLOCKED_DOMAINS = "domains_blocked"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

SENSOR_DICT = {
    "ads_blocked_today": ["Ads Blocked Today", "ads", "mdi:close-octagon-outline"],
    "ads_percentage_today": [
        "Ads Percentage Blocked Today",
        "%",
        "mdi:close-octagon-outline",
    ],
    "clients_ever_seen": ["Seen Clients", "clients", "mdi:account-outline"],
    "dns_queries_today": [
        "DNS Queries Today",
        "queries",
        "mdi:comment-question-outline",
    ],
    "domains_being_blocked": ["Domains Blocked", "domains", "mdi:block-helper"],
    "queries_cached": ["DNS Queries Cached", "queries", "mdi:comment-question-outline"],
    "queries_forwarded": [
        "DNS Queries Forwarded",
        "queries",
        "mdi:comment-question-outline",
    ],
    "unique_clients": ["DNS Unique Clients", "clients", "mdi:account-outline"],
    "unique_domains": ["DNS Unique Domains", "domains", "mdi:domain"],
}

SENSOR_LIST = list(SENSOR_DICT)
