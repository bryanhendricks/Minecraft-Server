import keyring
import getpass

service_id = 'minecraft_webserver'

# Set username
username = 'scambot'

# Get password
password = getpass.getpass()

# save password
keyring.set_password(service_id, username, password)
