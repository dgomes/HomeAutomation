#ifndef _REMOTE_H_
#define _REMOTE_H_

#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
     
int make_socket (uint16_t port);
int acceptRemote(int fd); 

#endif 
