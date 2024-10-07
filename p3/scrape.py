# project: p3
# submitter: Smwells3
# partner: none
# hours: 13

import os, zipfile, time, pandas
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        if node not in self.visited:
            #self.todo.extend(self.go(node)) need to insert children of node to left of existing self.todo ==> a stack
            self.dfstodo = self.go(node) + self.dfstodo
            self.visited.add(node)
            while len(self.dfstodo) > 0:
                self.dfs_search(self.dfstodo.pop(0))

    def bfs_search(self, node):
        self.bfstodo.extend(self.go(node))
        self.visited.add(node)
        while len(self.bfstodo) > 0:
            node = self.bfstodo.popleft()
            if node not in self.visited:
                self.bfstodo.extend(self.go(node))
                self.visited.add(node)

class FileScraper(GraphScraper):
    def __init__(self):
        self.dfstodo = []
        self.bfstodo = deque()
        super().__init__()
        if not os.path.exists("Files"):
            with zipfile.ZipFile("files.zip") as zf:
                zf.extractall()

    def go(self, node):
        with open(os.path.join("Files", node + ".txt")) as f:
            data = f.read()
        lines = data.split("\n")
        self.BFSorder.append(lines[2].split()[1])
        self.DFSorder.append(lines[3].split()[1])
        return lines[1].split()
    
class WebScraper(GraphScraper):
    # required
    def	__init__(self, driver=None):
        super().__init__()
        self.driver = driver
        self.dfstodo = []
        self.bfstodo = deque()
        self.BFSorder = ""
        self.DFSorder = ""

    def go(self, url):
        self.driver.get(url)
        bfs_btn = self.driver.find_element_by_id("BFS")
        dfs_btn = self.driver.find_element_by_id("DFS")
        bfs_btn.click()
        dfs_btn.click()
        self.BFSorder += bfs_btn.text
        self.DFSorder += dfs_btn.text
        links = self.driver.find_elements_by_tag_name("a")
        return([link.get_attribute("href") for link in links])
    
    def dfs_pass(self, start_url):
        self.visited = set()
        self.dfstodo = []
        self.DFSorder = ""
        self.dfs_search(start_url)
        return self.DFSorder

    def bfs_pass(self, start_url):
        self.visited = set()
        self.bfstodo = deque()
        self.BFSorder = ""
        self.bfs_search(start_url)
        return self.BFSorder
    
    def protected_df(self, url, password):
        self.driver.get(url)
        pwd_box = self.driver.find_element_by_id("password-input")
        pwd_box.clear()
        pwd_box.send_keys(password)
        pwd_btn = self.driver.find_element_by_id("attempt-button")
        pwd_btn.click()
        time.sleep(0.5)
        morebtn = self.driver.find_element_by_id("more-locations-button")
        for i in range(10):
            morebtn.click()
            time.sleep(0.1)
        data = pandas.read_html(self.driver.page_source)
        return data[0]