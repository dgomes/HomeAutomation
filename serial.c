#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <arduino-serial-lib.h>
#include <time.h>

#define DEBUG
#include "serial.h"
#include "update.h"
#include "json.h"
#include "utils.h"
#include "config.h"
#include "remote.h"

int setupSerial(char *port, int baudrate) {
	int fd = -1;

	fd = serialport_init(port, baudrate);
	if( fd==-1 ) {
		fprintf(stderr,"couldn't open port %s @ %d bauds\n", port, baudrate);
		return -1;
	}
	debug_print("opened port %s @ %d bps\n",port, baudrate);

	serialport_flush(fd);
	return fd;
};

int readSerial(int fd, char *buf, int buf_max, int timeout) {
	char eolchar = '\n';

	bzero(buf,buf_max);  
	int sr = serialport_read_until(fd, buf, eolchar, buf_max, timeout);
	debug_print("DEBUG:%d\t%s", sr, buf);

	return sr;
};

int arduinoEvent(char *buf, struct last_update *last, struct config *cfg) {
	time_t now = last->time;
	if(checkJSON_integer(buf,"code", 200)==0) {
		now = time(NULL);
	};
	if((now - last->time > cfg->xively.updaterate) && strlen(buf)>0) {
		int r;
		if(r = updateFeed(cfg->xively.key, cfg->xively.feedid, buf)) {
			printf("FAILED updated: %d\n", r);
		} else {
			printf("updated\n");
			strcpy(last->buf, buf);
			last->time = time(NULL);
		};
	};
	bzero(buf,BUF_MAX); 
	return 0; 
}

int main( int argc, const char* argv[] ) {
	struct config cfg;
	
	char conf[strlen(argv[0] + 10)];
	strcat(strcpy(conf,argv[0]), ".json");
	if(readConfig(conf, &cfg)) {
		//can't find configuration file in current dir, lookup in /etc/
		strcat(strcat(strcpy(conf, "/etc/"), argv[0]), ".json");
		fprintf(stderr,"Reading configuration from %s\n", conf);
		if(readConfig(conf,&cfg)) 
			// no configuration file supplied
			exit(1);	
	}

	int arduino_fd = setupSerial(cfg.port.name, cfg.port.speed);
	if(arduino_fd < 0)
		exit(2);

	int remote_fd = make_socket(cfg.remote.port);
	if(listen(remote_fd, 1) < 0)	
		exit(3);

	fd_set active_fd_set, read_fd_set;
	/* Initialize the set of active sockets. */
	FD_ZERO (&active_fd_set);
	FD_SET (arduino_fd, &active_fd_set);
	FD_SET (remote_fd, &active_fd_set);
	
	char buf[BUF_MAX];
	bzero(buf,BUF_MAX);  
	
	struct last_update last;
	last.time = time(NULL);
	last.buf = malloc(BUF_MAX);
	bzero(last.buf,BUF_MAX);  

	int nbytes;

	while(1) { 
		/* Block until input arrives on one or more active sockets. */ 
		read_fd_set = active_fd_set; 
		if (select (FD_SETSIZE, &read_fd_set, NULL, NULL, NULL) < 0) { 
			fprintf(stderr, "Error in select\n"); 
			exit (EXIT_FAILURE); 
		}	
		
		/* Service all the sockets with input pending. */
		int i; 
		for (i = 0; i < FD_SETSIZE; ++i) 
			if (FD_ISSET (i, &read_fd_set)) {
				if(i == arduino_fd) {
					if(!readSerial(arduino_fd, buf, BUF_MAX, cfg.port.timeout)) {
						arduinoEvent(buf, &last, &cfg);
						serialport_flush(arduino_fd);
					}
				} else if(i == remote_fd) {
					int new = acceptRemote(i);
					FD_SET (new, &active_fd_set);
				} else {
					nbytes = read(i, buf, BUF_MAX);
					if (nbytes < 0) {
						/* Read error. */
						perror ("read");
						exit (EXIT_FAILURE);
					} else if (nbytes == 0) {
						/* End-of-file. */
						close(i);
						FD_CLR(i, &active_fd_set);
					} else {
						/* Data read. */
						fprintf (stderr, "Server: got message: `%s'\n", buf);
						if(!strcmp(buf, "exit")) {
							return EXIT_SUCCESS;
						}
						serialport_write(arduino_fd, buf);
					}
					
				}
			}
	};
	return EXIT_SUCCESS;
}
