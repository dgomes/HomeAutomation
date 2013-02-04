all: snmp.so

snmp.so: snmp.o
	$(CC) -shared `python-config --ldflags` snmp.o -lnetsnmp -lcrypto -o $@ 
.c.o:
	$(CC) `python-config --cflags` -c $< -o $@ 
clean:
	rm -f *.o *.so *.pyc
