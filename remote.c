#include "remote.h"

int make_socket (uint16_t port) {
	int sock;
	struct sockaddr_in name;

	/* Create the socket. */
	sock = socket (PF_INET, SOCK_STREAM, 0);
	if (sock < 0)
	{
		fprintf(stderr, "%s: Can't create socket\n", __FILE__);
		exit (EXIT_FAILURE);
	}

	int on = 1;
	int ret = setsockopt( sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on) );
	if (ret < 0)
		perror("socket reuseaddr");

	/* Give the socket a name. */
	name.sin_family = AF_INET;
	name.sin_port = htons (port);
	name.sin_addr.s_addr = htonl (INADDR_ANY);
	if (bind (sock, (struct sockaddr *) &name, sizeof (name)) < 0)
	{
		fprintf(stderr, "%s: Can't bind socket\n", __FILE__);
		exit (EXIT_FAILURE);
	}
	fprintf(stderr, "listennig on port %d\n",port);

	return sock;
}

int acceptRemote(int fd) {
	/* Connection request on original socket. */
	int new;
	struct sockaddr_in clientname;
	size_t size = sizeof (clientname);
	new = accept (fd, (struct sockaddr *) &clientname, &size);
	if (new < 0) {
		perror ("accept");
		exit (EXIT_FAILURE);
	}
	fprintf (stderr, "Server: connect from host %s, port %d.\n", inet_ntoa (clientname.sin_addr), ntohs (clientname.sin_port));
	return new;	
}


