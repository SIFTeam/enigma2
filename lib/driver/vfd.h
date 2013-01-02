#ifndef VFD_H_
#define VFD_H_

class evfd
{
protected:
	static evfd *instance;
#if defined(HAVE_GIGABLUE_TEXTLCD)
	int file_vfd;
#endif
#ifdef SWIG
	evfd();
	~evfd();
#endif
public:
#ifndef SWIG
	evfd();
	~evfd();
#endif
	void init();
	static evfd* getInstance();

	void vfd_write_string(char * string);
	void vfd_led(char * led);
	void vfd_symbol_network(int net);
	void vfd_symbol_circle(int cir);
};


#endif
