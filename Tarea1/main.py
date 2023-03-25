import socket

def get_data_image(s: socket.socket,host,port):
    s.sendto("GET NEW IMG DATA".encode(),(host,port))
    return s.recvfrom(1024)[0].decode()
    
def data_to_dict(data):
    d = {}
    data = data.strip().split(" ")
    c = 0
    for key_and_value in data:
        key,value = key_and_value.split(":")
        d[key] = value
        if "P" in key and ("TCP" in key or "UDP" in key):
            c += 1;
    d["PARTS"] = c
    return d

def get_p1tcp(host,port,data):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,port))
    
    parts = data["PARTS"]
    ID = data["ID"]

    s.send(f"GET 1/{parts} IMG ID:{ID}".encode())

    response = s.recv(int(data["W"])*int(data["H"])*3)
    s.close()
    return response

def get_pudp(s,host,port,data,part):

    parts = data["PARTS"]
    ID = data["ID"]

    s.sendto(f"GET {part}/{parts} IMG ID:{ID}".encode(),(host,port))
    return s.recvfrom(int(data["W"])*int(data["H"])*3)[0]

# addres and port
HOST = "jdiaz.inf.santiago.usm.cl"
PORT = 50006

# create socket and bind
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# get image data from host
data_img = get_data_image(s_udp,HOST,PORT)

data_img = data_to_dict(data_img)

p1tcp = get_p1tcp(HOST,int(data_img["P1TCP"]),data_img)
img_binary = p1tcp

p2tcp = get_pudp(s_udp,HOST,int(data_img["P2UDP"]),data_img,2)
img_binary += p2tcp

if data_img["PARTS"] > 2:
    p3tcp = get_pudp(s_udp,HOST,int(data_img["P3UDP"]),data_img,3)
    img_binary += p3tcp

file = open("output.png","wb")
file.write(img_binary)
file.close()
