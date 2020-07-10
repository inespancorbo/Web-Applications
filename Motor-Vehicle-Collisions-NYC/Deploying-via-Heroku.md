# Deploying Streamlit via Heroku

1. Create a requieremtns.txt file:

Install (if unavailable) and include path to codebase

``pip install pipreqs``

``pipreqs <directory path>``

2. setup.sh and Procfile:

Save the following in codebase as setup.sh. Make sure to change to relevant email.

```
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

3. Create Procfile

``echo "web: sh setup.sh && streamlit run app.py" >> Procfile.txt``

4. Login to Heroku

Login into the CLI using your Heroku account. For this open a terminal, move into the application folder and then execute heroku login.

```
(base) Iness-MBP-2:~ inespancorbo$ heroku login
heroku: Press any key to open up the browser to login or q to exit: 
Opening browser to https://cli-auth.heroku.com/auth/cli/browser/a1356fd5-7315-42dd-93c3-5eb76628b304
Logging in... done
Logged in as <user>
```
