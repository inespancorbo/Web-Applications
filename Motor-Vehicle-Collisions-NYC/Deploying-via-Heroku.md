1. Create a requieremtns.txt file:

Install (if unavailable) and include path to codebase

``pip install pipreqs``

``pipreqs <directory path>``

2. setup.sh and Procfile:

Save the following in codebase as setup.sh. Make sure to change to relevant email.

```mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml```
