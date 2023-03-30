import socket

def get_data_image(s: socket.socket,host,port):
    s.sendto("GET NEW IMG DATA".encode(),(host,port))
    respuesta = s.recvfrom(1024)[0].decode()
    print("Mensaje Recibido: " + respuesta)
    return respuesta
    
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
    print("Mensaje enviado a: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> por <TCP>: " + f"GET 1/{parts} IMG ID:{ID}")

    response = s.recv(int(data["W"])*int(data["H"])*3)
    s.close()
    print("Mensaje recibido de: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> por <TCP>: Bytes recibidos")
    return response

def get_pudp(s,host,port,data,part):
    parts = data["PARTS"]
    ID = data["ID"]

    s.sendto(f"GET {part}/{parts} IMG ID:{ID}".encode(),(host,port))
    print("Mensaje enviado a: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> por <UDP>: " + f"GET {part}/{parts} IMG ID:{ID}")

    print("Mensaje recibido de: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> por <UDP>: Bytes recibidos")

    return s.recvfrom(int(data["W"])*int(data["H"])*3)[0]

def verify_img(host,port,data,data2):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((host,int(port)))

    s.send(data)

    print("Mensaje enviado a: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> por <TCP>: Bytes Imagen")
    response = s.recv(int(data2["W"])*int(data2["H"])*3)
    aux = response.decode()
    print("Mensaje recibido de: <jdiaz.inf.santiago.usm.cl>:<" + str(port) + "> port <TCP>: " + aux)
    
    if '200: SUCCESS' in aux:
        print("Imagen Coincide: " + aux)
        return 1
        s.close()
    else:
        print("Imagen contiene error: " + aux)
        return 0
        s.close()

while(1):
    # addres and port
    HOST = "jdiaz.inf.santiago.usm.cl"
    PORT = 50006

    # create socket and bind
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("** NUEVO INTENTO **")

    # get image data from host
    data_img = get_data_image(s_udp,HOST,PORT)

    data_img = data_to_dict(data_img)

    p1tcp = get_p1tcp(HOST,int(data_img["P1TCP"]),data_img)
    p2tcp = get_pudp(s_udp,HOST,int(data_img["P2UDP"]),data_img,2)
    if data_img["PARTS"] > 2:
        p3tcp = get_pudp(s_udp,HOST,int(data_img["P3UDP"]),data_img,3)

    print("Iniciando escritura de imagen")

    img_binary = p1tcp
    img_binary += p2tcp
    if(data_img["PARTS"] > 2):
        img_binary += p3tcp

    condicional = verify_img(HOST, data_img["PV"], img_binary,data_img)

    if(condicional == 1):
        print("Escritura de imagen finalizada")

        nombre = data_img["ID"] + ".png"
        file = open(nombre,"wb")
        file.write(img_binary)
        file.close()
        print("** FIN **")
        break
    print("Escritura de imagen fallida, intentando nuevamente")