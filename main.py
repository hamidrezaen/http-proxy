from socket import *
from _thread import *


# thread function
# receiving the data from the client
# parse the data and extract method, url and port
# if method is CONNECT
# then send 200 Connection Established
# else send the data to the server without the url
# At last, run the proxy server
def threaded(connection):
    data = connection.recv(2048)
    decode_data = data.decode('utf-8').split('\n')

    data_first_line = decode_data[0].split(' ')
    method = data_first_line[0]
    url = data_first_line[1]

    if method == 'CONNECT':
        url = url.split(':')
        port = int(url[1])
        url = url[0]
        connection.send('HTTP/1.1 200 Connection Established\n\n'.encode('utf-8'))
        data = connection.recv(2048)
        run_proxy_server(connection, url, port, data)
    else:
        url = url.split('://')[1]
        url = url.split(':')
        if len(url) == 1:
            port = 80
        else:
            port = int(url[1])

        url = url[0]

        data = (method + ' /' + url.split('/')[1] + ' ' + data_first_line[2] + '\n').encode('utf-8')
        data += ('\n'.join(decode_data[1:])).encode('utf-8')
        run_proxy_server(connection, url, port, data)


# run the proxy server
def run_proxy_server(connection, url, port, data):
    s = socket(AF_INET, SOCK_STREAM)
    # connect to the server
    s.connect((url, port))
    # send the data to the server
    s.send(data)

    while True:
        # receive the data from the server
        reply = s.recv(4096)
        # if the data is empty, then close the connection
        if len(reply) > 0:
            # send the data to the client
            connection.send(reply)
            # receive the data from the client
            data = connection.recv(2048)
            # send the data to the server
            s.send(data)

            # if the data is empty, then close the connection
            if len(data) == 0:
                print('Client closed the connection.')
                break
        else:
            print('Server closed the connection.')
            break

    s.close()
    connection.close()


# creating socket and binding it to port 12345
host = ''
port = 12345
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind((host, port))
print('socket binded to port', port)

server_socket.listen(5)
print('socket is listening')

while True:
    try:
        connection, address = server_socket.accept()
        print('Connected to :', address[0], ':', address[1])
        start_new_thread(threaded, (connection,))
    except:
        print('Turning off the http proxy')
        server_socket.close()
        break
