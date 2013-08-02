LIBRARY_DIRS=-L libs/libxively/src/libxively/
XIVELY_INCLUDE_DIR=-I libs/libxively/src/libxively/
LIB_XIVELY=libs/libxively/src/libxively/libxively.a

ARDUINO_SERIAL_INCLUDE_DIR=-I libs/arduino-serial/
LIB_ARDUINO_SERIAL=libs/arduino-serial/arduino-serial-lib.o

LIBRARIES=$(LIB_XIVELY) $(LIB_ARDUINO_SERIAL) `pkg-config --libs jansson`
INCLUDE_DIRS=$(XIVELY_INCLUDE_DIR) $(ARDUINO_SERIAL_INCLUDE_DIR) `pkg-config --cflags jansson`

CFLAGS=-O2

SOURCES	:= $(wildcard *.c) 
OBJS	:= $(SOURCES:.c=.o) 

%.o : %.c
	$(CC) $(INCLUDE_DIRS) -c $(CFLAGS) $< -o $@

homeautomation: $(OBJS)
	$(CC) $(LIBRARY_DIRS) -o $@ $(LDFLAGS) $^ $(LIBRARIES)

clean:
	rm $(OBJS) homeautomation 

all: homeautomation 
