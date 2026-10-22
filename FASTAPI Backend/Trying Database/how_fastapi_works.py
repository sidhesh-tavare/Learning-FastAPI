from typing import Callable,Any

routes : dict[str,Callable[[Any],Any]] = {}

def route(path :str):
    def register_route(func):
        routes[path] = func
        return func 
    return register_route


@route("/shipment")
def get_shipment():
    return "Shipment in delivery "

@route("/cancel")
def cancel():
    return "Cancelled "

request : str = ""
# print(routes)
while request != "quit":
    request = input(">")
    if request in routes:
        response : Callable = routes[request]
        print(response())
    else:
        print("NotFound")

