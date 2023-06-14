import markdown, os, requests, time, json, csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import List

class URLGenerator:
    def __init__(self, lang: str):
        self.lang = lang
        self.org = ""
        self.msvc_extension = ["ixx"]
        self.clang_extension = ["cppm", "ccm", "cxxm"]
        self.gcc_extension = ["cxx"]

    def query(self) -> str:
        res = ""
        if self.lang:
            res = "language:" + self.lang
        
        if self.org:
            res = res + "+org:" + self.org

        extension_list = ["+path:*." + extension for extension in self.msvc_extension + self.clang_extension + self.gcc_extension]

        extension_query = ""
        for i, e in enumerate(extension_list):
            if i != len(extension_list) - 1:
                extension_query = extension_query + e + "+OR"
            else:
                extension_query = extension_query + e

        res = res + extension_query
        res  = res + "&type=code"

        return res

class Result:
    def __init__(self, text: str, url: str, endpoint: str, has_module: bool, json: str, search_endpoint: str):
        self.text = text
        self.url = url
        self.endpoint = endpoint
        self.has_module = has_module
        self.json = json
        self.search_endpoint = search_endpoint

def read_README() -> List:
    with open('../awesome-cpp/README.md', 'r') as fin:
        rendered = fin.read()

    ast = markdown.markdown(rendered)
    soup = BeautifulSoup(ast, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if "github.com" in url:
            links.append({
                'text': link.text,
                'url': url
            })
    
    return links

def create_queries(github_urls):
    queries = dict()

    for url in github_urls:
        parsed_url = urlparse(url["url"])
        path = parsed_url.path

        if len(path.split("/")) < 2:
            continue
        splitedPath = list(filter(lambda x: x != "", path.split("/")))
        generator = URLGenerator(lang="cpp")  
        
        if len(splitedPath) < 1:
            continue
        else:
            generator.org = splitedPath[0]
        
        queries[generator.query()] = (url["text"], f"https://github.com/{splitedPath[0]}")
        # queries.add((generator.query(), url["text"], url["url"]))
    
    return queries

def request_search_api():
    results = []
    count = 0
    for k, v in queries.items():
        # The REST API has a custom rate limit for searching. For authenticated requests, you can make up to 30 requests per minute for all search endpoints except for the "Search code" endpoint. 
        # The "Search code" endpoint requires you to authenticate and limits you to 10 requests per minute. 
        # For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute.
        # ref: https://docs.github.com/en/rest/search?apiVersion=2022-11-28
        if count != 0 and count % 9 == 0:
            time.sleep(61)        

        query = k
        url = "https://api.github.com/search/code?q={}".format(query)

        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer <personal access token>"
        }

        response = requests.get(url, headers=headers)
        jsonData = response.json()
        
        if response.status_code == 200:
            res = Result(text = v[0], 
                         url = v[1], 
                         endpoint=url, 
                         has_module = jsonData["total_count"] != 0, 
                         json=json.dumps(jsonData), 
                         search_endpoint="https://github.com/search?q=" + query)
            results.append(res)
            print(count, "hasModule", res.has_module, res.search_endpoint)
        else:
            print("Error:", response.status_code, jsonData["message"])
        count += 1

    return results

def create_csv(results):
    csv_file = "results.csv"
    fieldnames = ["text", "url", "endpoint", "has_module", "json", "search_endpoint"]

    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                "text": result.text,
                "url": result.url,
                "has_module": result.has_module,
                "endpoint": result.endpoint,
                "json": result.json,
                "search_endpoint": result.search_endpoint
            })

# read and extract url from Awesome cpp repository's README
github_urls = read_README()

# create query for searhcing the c++ module file extension.("ixx", "cppm", "ccm", "cxxm", "cxx")
# All major C++ compilers(clang, gcc, MSVC) define different file extensions for defining modules. 
# So, if the projects contain files for modules, we can say that they use C++20 Modules.
queries = create_queries(github_urls)

# print(queries)
# request search API and get the response
results = request_search_api()

# save the result in CSV file
create_csv(results)
