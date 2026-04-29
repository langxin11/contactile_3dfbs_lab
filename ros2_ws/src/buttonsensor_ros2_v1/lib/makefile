exe: USER_APP_EXAMPLE.o
	g++ -std=c++17 -L./ -lm -o USER_APP_EXAMPLE USER_APP_EXAMPLE.o -lPTSDK -lpthread

USER_APP_EXAMPLE.o:
	g++ -std=c++17 -I./ -c USER_APP_EXAMPLE.cpp

clean:
	rm USER_APP_EXAMPLE.o
	rm USER_APP_EXAMPLE
