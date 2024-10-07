import netaddr, time, sys, json, zipfile, csv, geopandas, re, os
import pandas as pd
from zipfile import ZipFile
from io import TextIOWrapper, BytesIO
from collections import defaultdict
from matplotlib import pyplot as plt

df = pd.read_csv("ip2location.csv")

def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        print(json.dumps(ip_test(ips), indent=1))
    
    elif sys.argv[1] == "sample":
        zip1 = sys.argv[2]
        zip2 = sys.argv[3]
        stride = sys.argv[4]
        sampling(zip1, zip2, stride)
        
    elif sys.argv[1] == "world":
        world_func(sys.argv[2], sys.argv[3])
    
    elif sys.argv[1] == "phone":
        phone_numbers(sys.argv[2])
    
    else:
        print("unknown command: "+sys.argv[1])
        
def dict_creator(ip, index, t0):
    info = {}
    info["ip"] = ip 
    info["int_ip"] = int(netaddr.IPAddress(ip)) 
    info["region"] = df["region"][index] 
    info["ms"] = (time.time() - t0) * 1000
    return info

def ip_test(ips, index=0, result=list()):
    last_index = 0
    while len(ips) > 0:
        info = {}
        ip = ips.pop(0)
        index %= (len(df) - 1)
        t0 = time.time()
        if df["low"].at[last_index] <= int(netaddr.IPAddress(ip)) <= df["high"].at[last_index]:
            result.append(dict_creator(ip, last_index, t0))
        else:
            for low in df["low"][index:]:
                if low <= int(netaddr.IPAddress(ip)) <= df["high"].at[index]:
                    result.append(dict_creator(ip, index, t0))
                    last_index = index
                else:
                    index += 1
    return result

def zip_csv_iter(name):
    with ZipFile(name) as zf:
        with zf.open(name.replace(".zip", ".csv")) as f:
            reader = csv.reader(TextIOWrapper(f))
            for row in reader:
                yield row
        
def ip_sorting(instance):
    digits = instance.split(".")
    first_digits = int(digits[0])
    second_digits = int(digits[1])
    third_digits = int(digits[1])
    return (first_digits, second_digits, third_digits)

def sample_sorting(instance):
    digits = instance[0].split(".")
    first_digits = int(digits[0])
    second_digits = int(digits[1])
    third_digits = int(digits[2])
    return (first_digits, second_digits, third_digits)

def sampling(zip1, zip2, stride=30000):
    reader = zip_csv_iter(zip1)
    header = next(reader)
    header.append("region")
    ip_idx = header.index("ip")
    samples = []
    ips = []
    while True:
        row = next(reader)
        samples.append(row)
        ip_str = ""
        for character in row[ip_idx]:
            if character.isalpha():
                ip_str += "0"
            else:
                ip_str += character
        ips.append(ip_str)
        for i in range(int(stride)-1):
            try:
                next(reader)
            except StopIteration:
                ips.sort(key=ip_sorting) 
                samples.sort(key=sample_sorting)
                data = ip_test(ips, 0, [])
                for sample_idx in range(len(samples)):
                    samples[sample_idx].append(data[sample_idx]["region"])
                with ZipFile(zip2, "w") as zf:
                    with zf.open(zip2.replace(".zip", ".csv"), "w") as raw:
                        with TextIOWrapper(raw) as f:
                            writer = csv.writer(f, lineterminator='\n')
                            writer.writerow(header) # write the row of column names to zip2
                            for row in samples:
                                writer.writerow(row) # write a row to zip2
                return    

def country_counter(zip1):
    total = defaultdict(int)
    reader = zip_csv_iter(zip1)
    header = next(reader)
    for row in reader:
        total[row[-1]] += 1
    return pd.Series(total)
            
def world_func(zip1, file):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    total = country_counter(zip1)
    world["frequency"] = pd.Series(dtype=int)
    for country_idx in range(len(world["name"])):
        world.loc[country_idx, "frequency"] = 0
        try:
            world.loc[country_idx, "frequency"] = total[world.loc[country_idx, "name"]]
        except:
            continue
    fig, ax = plt.subplots(figsize=(15,15))
    world[world["continent"] != "Antarctica"].plot(ax=ax, column="frequency", cmap="plasma").get_figure().savefig(file,format="svg")
                       
def phone_numbers(zip1):    
    with ZipFile(zip1) as zf:
        numbers = set()
        for file_name in zf.namelist():
            with zf.open(file_name, "r") as f:
                tio = TextIOWrapper(f)
                string = tio.read()
                found = re.findall(r"((\()?\d{3}(\))?([-, " "]?)?\d{3}(-?)?\d{4})", string)
                for number in found:
                    if number[0][0] != "0":
                        numbers.add(number[0])
        for number in numbers:
            print(number)          
        
if __name__ == '__main__':
     main()