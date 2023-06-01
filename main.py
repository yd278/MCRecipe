import json
import os
import math
from queue import Queue
class Recipe:
    def __init__(self, name : str) -> None:
        self.name : str = name
        self.components : dict[str,float] = {}
        self.available : dict[str,bool]= {}
        self.requirement: float = 0.0
        self.in_stock : float = 0.0
        self.visited : bool = False

    def check_avail(self) -> bool:
        result : bool = True
        for _,avail in self.available.items():
            result = result and avail
        return result

def query_recipe(name : str, lookup : dict[str,Recipe], q : Queue[str])-> None:
    filename = "cache/"+name+".json"
    if(os.path.exists(filename)):
        with open(filename,"r") as f:
            json_text = f.read()
            lookup[name].components = json.loads(json_text)
            for comp_name in lookup[name].components.keys():
                lookup[name].available[comp_name]=False
    else:
        print("Enter the name and quantity of each required component of "+name +" on each line, ending with a blank line.")
        line : str = input()
        while line != "" :
            splitted = line.split(' ')
            comp_name : str = splitted[0]
            quantity : float = float(splitted[1])
            lookup[name].components[comp_name] =quantity
            lookup[name].available[comp_name] = False
            line = input()
        with open(filename,"w") as f:
            f.write(json.dumps(lookup[name].components))

if __name__ == "__main__":
    lookup : dict[str,Recipe] = {}
    print("Target item:\n")
    target_name : str = input()
    input_q : Queue[str]  = Queue()
    input_q.put(target_name)

    lookup[target_name] = Recipe(target_name)
    while not input_q.empty():
        curr_name = input_q.get()
        query_recipe(curr_name,lookup,input_q)
        for comp_name in lookup[curr_name].components.keys():
            if not comp_name in lookup:
                input_q.put(comp_name)
                lookup[comp_name] = Recipe(comp_name)
    
    craft_layers : list[list[str]]= []
    layer = 0

    while (True):
        curr_layer :list[str] = []
        for name ,recipe in lookup.items():
            if(recipe.check_avail() and not recipe.visited):
                curr_layer.append(name)
                recipe.visited = True  
        if len(curr_layer)==0:
            break
        craft_layers.append(curr_layer)
        for comp in curr_layer:
            for _,recipe in lookup.items():
                if comp in recipe.available:
                    recipe.available[comp] = True
        layer += 1
    
    top = layer - 1

    for l in range(top, -1, -1):
        for name in craft_layers[l]:
            print("How many "+ name + " do you have?\n")
            num = float(input())
            lookup[name].in_stock = num


    lookup[target_name].requirement = 1
    for l in range(top, -1, -1):
        for cur_name in craft_layers[l]:
            req = lookup[cur_name].requirement
            in_stock = lookup[cur_name].in_stock
            if req > in_stock:
                req = math.ceil(req - in_stock)
            else:
                req = 0
            for name,quant in lookup[cur_name].components.items():
                lookup[name].requirement += req * quant

    with open("output.md","w") as f:
        for i in range(top + 1):
            f.write("\n## layer "+str(i)+"\n")
            for name in craft_layers[i]:
                f.write("- [ ] "+name + " " + str(lookup[name].requirement)+"\n")



