from kivy.storage.jsonstore import JsonStore

# Declare which json file to use and assign to the variable store
store = JsonStore('auth.json')

if store.exists('auth'):  # Check if key exists
    store.delete('auth')  # Delete key if it exists