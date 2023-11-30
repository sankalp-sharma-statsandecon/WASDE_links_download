import os
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

def get_supported_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    supported_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and (href.endswith('.csv') or href.endswith('.xls') or href.endswith('.xlsx') or href.endswith('.zip')):
            supported_links.append(urljoin(url, href))

    return supported_links

def download_file(url, destination):
    response = requests.get(url, timeout=30)
    with open(destination, 'wb') as file:
        file.write(response.content)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        website_url = request.form['website_url']
        destination_folder = request.form['destination_folder']

        supported_links = get_supported_links(website_url)

        messages = []  # Store messages for each file

        for i, link in enumerate(supported_links):
            file_extension = link.split(".")[-1]
            destination = os.path.join(destination_folder, f'file_{i + 1}.{file_extension}') if destination_folder else f'file_{i + 1}.{file_extension}'
            
            try:
                download_file(link, destination)
                messages.append(f'Successfully downloaded: {link} to {destination}')
            except Exception as e:
                messages.append(f'Failed to download {link}. Error: {str(e)}')
                print(f'Error downloading {link}: {str(e)}')

        return '<br>'.join(messages)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
