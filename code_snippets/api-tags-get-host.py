from dogapi import dog_http_api as api

api.api_key = '9775a026f1ca7d1c6c5af9d94d9595a4'
api.application_key = '87ce4a24b5553d2e482ea8a8500e71b8ad4554ff'

# Get tags by host name.
api.host_tags('web.example.com')

# Get tags by host id.
api.host_tags(101)
