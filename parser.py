import requests
import ray

# remote function that fetches the links from specific Wikipedia page, can be run in parallel
@ray.remote
def fetchLinks(title):
    session = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": "",
        "prop": "links",
        "pllimit": "max"
    }
    params["titles"] = title

    response = session.get(url=url, params=params)
    data = response.json()
    pages = data["query"]["pages"]

    page_titles = []

    for key, val in pages.items():
        try:
            for link in val["links"]:
                page_titles.append(link["title"])
        except KeyError:
            return None

    # if there are more pages left
    while "continue" in data:
        plcontinue = data["continue"]["plcontinue"]
        params["plcontinue"] = plcontinue

        response = session.get(url=url, params=params)
        data = response.json()
        pages = data["query"]["pages"]

        for key, val in pages.items():
            for link in val["links"]:
                page_titles.append(link["title"])

    return page_titles

# check if the destination page is in the list
def destFound(destPage, titles):
    for title in titles:
        if title == destPage:
            return True
    return False

# print the path from the start page to the destination page
def printResults(startPage, destPage, parentTitle, original_list, titles):
    if destPage in original_list:
        print(f"The path is: {startPage} -> {destPage}")
    elif parentTitle in original_list:
        print(f"The path is: {startPage} -> {parentTitle} -> {destPage}")
    # trace the path
    else:
        path = []
        path.append(parentTitle)
        i = 0
        while True:
            titleFound = False
            for key, val in titles.items():
                if val is not None:
                    for title in titles[key]:
                        if title == path[i]:
                            path.append(key)
                            if key in original_list:
                                print(f"The path is: {startPage}", end=" ")
                                for title in reversed(path):
                                    print(f"-> {title}", end=" ")
                                print(f"-> {destPage}")
                                return
                            i += 1
                            titleFound = True
                            break
                    if titleFound:
                        break

def main():
    # initialize Ray which implements parallelism and distribution
    ray.init()

    startPage = input("Starting page: ")
    destPage = input("Destination page: ")
    # distributed workers that fetch links in parallel
    workers = [None, None, None, None, None, None]
    workers[0] = fetchLinks.remote(startPage)
    titles_list = ray.get(workers[0])
    original_list = titles_list.copy()
    titles = {k: None for k in titles_list}
    titles_updated = {}
    new_titles = {}

    # if destination page is found
    if destFound(destPage, titles_list):
        printResults(startPage, destPage, startPage, original_list, titles)
        return 0

    # titles dictionary initialization
    while True:
        # start up to six workers to fetch links from found pages
        if len(titles_list) != 0:
            workers[0] = fetchLinks.remote(titles_list[0])
        if len(titles_list) > 1:
            workers[1] = fetchLinks.remote(titles_list[1])
        if len(titles_list) > 2:
            workers[2] = fetchLinks.remote(titles_list[2])
        if len(titles_list) > 3:
            workers[3] = fetchLinks.remote(titles_list[3])
        if len(titles_list) > 4:
            workers[4] = fetchLinks.remote(titles_list[4])
        if len(titles_list) > 5:
            workers[5] = fetchLinks.remote(titles_list[5])

        results = ray.get(workers)

        if len(titles_list) < 6:
            results_count = len(titles_list)
        else:
            results_count = len(results)

        for i in range(results_count):
            if results[i] is not None:
                titles[titles_list[i]] = results[i]
                # if destination page is found
                if destFound(destPage, results[i]):
                    printResults(startPage, destPage, titles_list[i], original_list, titles)
                    return 0

        if len(titles_list) > 6:
            for i in range(6):
                titles_list.pop(0)
            continue
        else:
            break

    titles_updated = titles.copy()

    # filling up titles dictionary    
    while True:
        for key, val in titles.items():
            if titles[key] is None:
                continue
            else:
                titles_list = titles[key]
                while True:
                    # start up to six workers to fetch links from found pages
                    if len(titles_list) != 0:
                        workers[0] = fetchLinks.remote(titles_list[0])
                    if len(titles_list) > 1:
                        workers[1] = fetchLinks.remote(titles_list[1])
                    if len(titles_list) > 2:
                        workers[2] = fetchLinks.remote(titles_list[2])
                    if len(titles_list) > 3:
                        workers[3] = fetchLinks.remote(titles_list[3])
                    if len(titles_list) > 4:
                        workers[4] = fetchLinks.remote(titles_list[4])
                    if len(titles_list) > 5:
                        workers[5] = fetchLinks.remote(titles_list[5])

                    results = ray.get(workers)

                    if len(titles_list) < 6:
                        results_count = len(titles_list)
                    else:
                        results_count = len(results)

                    for i in range(results_count):
                        if results[i] is not None:
                            titles_updated[titles_list[i]] = results[i]
                            new_titles[titles_list[i]] = results[i]
                            # if destination page is found
                            if destFound(destPage, results[i]):
                                printResults(startPage, destPage, titles_list[i], original_list, titles_updated)
                                return 0

                    if len(titles_list) > 6:
                        titles_list = titles_list[6:]
                        continue
                    else:
                        break
        titles = new_titles.copy()
        new_titles = {}
    
    return 0
        

if __name__ == '__main__':
    main()