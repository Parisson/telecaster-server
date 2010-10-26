/*
    Copyright (C) 2001 Paul Davis
    Copyright (C) 2003 Jack O'Quin
    
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

    This is the example JACK client that has been slightly modified to 
    call libedcast by oddsock.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>
#include <getopt.h>
#include <jack/jack.h>
#include <jack/ringbuffer.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include "libedcast/libedcast.h"

edcastGlobals	g;
int currentSamplerate = 0;
int currentChannels = 0;
int	changeMetadata = 0;
char	oldcurrentTitle[1024] = "";
char	currentTitle[1024] = "";
int	getFirstTwo = 0;
char	portMatch[255] = "";

typedef struct _thread_info {
    pthread_t thread_id;
    pthread_t md_thread_id;
    pthread_t reconnect_thread_id;
    jack_nframes_t duration;
    jack_nframes_t rb_size;
    jack_client_t *client;
    unsigned int channels;
    int bitdepth;
    char *path;
    volatile int can_capture;
    volatile int can_process;
    volatile int status;
} jack_thread_info_t;

/* JACK data */
unsigned int nports;
jack_port_t **ports;
//jack_default_audio_sample_t **in;
jack_nframes_t nframes;
const size_t sample_size = sizeof(jack_default_audio_sample_t);

/* Synchronization between process thread and edcast thread. */
#define DEFAULT_RB_SIZE 16384*2		/* ringbuffer size in frames */
jack_ringbuffer_t **rb;
pthread_mutex_t edcast_thread_lock = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t  data_ready = PTHREAD_COND_INITIALIZER;
long overruns = 0;
int generalFlag = 1;
int serverFlag = 1;
int outputFlag = 1;


void setLogFlags() {
	if (strstr(g.outputControl, "GENERAL")) {
		generalFlag = 1;
	}
	if (strstr(g.outputControl, "SERVER")) {
		serverFlag = 1;
	}
	if (strstr(g.outputControl, "OUTPUT")) {
		outputFlag = 1;
	}
}
void generalStatusCallback(void *g, void *pValue) {
	if (generalFlag) {
		printf("GENERAL: %s\n", (char *)pValue);
	}
}
void serverStatusCallback(void *g, void *pValue) {
	if (serverFlag) {
		printf("SERVER: %s\n", (char *)pValue);
	}
}
void writeBytesCallback(void *g, void *pValue) {
	// pValue is a long
	static  long    startTime = 0;
	static  long    endTime = 0;
	static  long    bytesWrittenInterval = 0;
	static  long    totalBytesWritten = 0;
	static  int initted = 0;
	char    kBPSstr[255] = "";

	if (!outputFlag) {
		return;
	}

	if (!initted) {
		initted = 1;
		memset(&startTime, '\000', sizeof(startTime));
		memset(&endTime, '\000', sizeof(endTime));
		memset(&bytesWrittenInterval, '\000', sizeof(bytesWrittenInterval));
		memset(&totalBytesWritten, '\000', sizeof(totalBytesWritten));
	}
        long        bytesWritten = (long)pValue;

        if (bytesWritten == -1) {
		strcpy(kBPSstr, "");
    		printf("OUTPUT: %s\n", (char *)kBPSstr);
		startTime = 0;
		return;
	}
	if (startTime == 0) {
		startTime = time(&(startTime));
		bytesWrittenInterval = 0;
	}
	bytesWrittenInterval += bytesWritten;
	totalBytesWritten += bytesWritten;
	endTime = time(&(endTime));
	if ((endTime - startTime) > 2) {
		int bytespersec = bytesWrittenInterval/(endTime - startTime);
		long kBPS = (bytespersec * 8)/1000;
		sprintf(kBPSstr, "%ld Kbps", kBPS);
		printf("OUTPUT: %s\n", (char *)kBPSstr);
		startTime = 0;
	}
}


void *
edcast_metadata_thread (void *arg)
{
	while (1) {
		if (strlen(g.externalFile) == 0) {
			return 0;
		}
		FILE *filep = fopen(g.externalFile, "r");
		if (filep) {
			char buffer[1024];
			memset(buffer, '\000', sizeof(buffer));
			fgets(buffer, sizeof(buffer)-1, filep);
			char *p1;
			p1 = strstr(buffer, "\r\n");
			if (p1) {
				*p1 = '\000';
			}

			p1 = strstr(buffer, "\n");
			if (p1) {
				*p1 = '\000';
			}
			if (g.weareconnected) {
				if (strcmp(oldcurrentTitle, buffer)) {
					strcpy(currentTitle, buffer);
					strcpy(oldcurrentTitle, buffer);
					changeMetadata = 1;
				}
			}
			fclose(filep);
		}
		sleep(1);
	}

	return 0;
}

void *
edcast_reconnect_thread (void *arg)
{
	while (1) {
		time_t currentTime = time(&currentTime);
		if (g.forcedDisconnect) {
			int timeout = getReconnectSecs(&g);
			int timediff = currentTime - g.forcedDisconnectSecs;
			if (timediff > timeout) {
				connectToServer(&g);
				memset(oldcurrentTitle,'\000', sizeof(oldcurrentTitle));
			}
			else {
				char buf[255] = "";
				sprintf(buf, "Connecting in %d seconds", timeout - timediff);
				serverStatusCallback(&g, buf);
			}
		}
		sleep(1);
	}


	return 0;
}

void *
edcast_thread (void *arg)
{
	jack_thread_info_t *info = (jack_thread_info_t *) arg;
	static jack_nframes_t total_captured = 0;
	//jack_nframes_t samples_per_frame = info->channels * 2048;
	jack_nframes_t samples_per_frame = 2048;
	size_t bytes_per_frame = samples_per_frame * sample_size;
	float *framebuf_r = (float *)malloc (bytes_per_frame);
	float *framebuf_l = (float *)malloc (bytes_per_frame);
	float *framebuf = (float *)malloc (bytes_per_frame*2);

	pthread_setcanceltype (PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
	pthread_mutex_lock (&edcast_thread_lock);

	info->status = 0;

	while (1) {

/*
		if (rb) {
			int x = jack_ringbuffer_read_space (rb[0]);
			printf("We've got %d in the ringbuffer\n", x);
		}
*/
		while (info->can_capture &&
		       (jack_ringbuffer_read_space (rb[0]) >= bytes_per_frame)) {

			jack_ringbuffer_read (rb[0], (char *)framebuf_r, bytes_per_frame);
			if (currentChannels == 2) {
				jack_ringbuffer_read (rb[1], (char *)framebuf_l, bytes_per_frame);
			}
			int samplecounter = 0;
			for (int i=0;i<samples_per_frame;i++) {
				framebuf[samplecounter] = framebuf_r[i];
				samplecounter++;
				if (currentChannels == 2) {
					framebuf[samplecounter] = framebuf_l[i];
					samplecounter++;
				}
			}
	
			handle_output(&g, (float *)framebuf, samples_per_frame, currentChannels, currentSamplerate);
			if (changeMetadata) {
				char buf[1024] = "";
				setCurrentSongTitleURL(&g, currentTitle);

				sprintf(buf, "Changing metadata to %s", currentTitle);
				serverStatusCallback(&g, (void *)buf);
				changeMetadata = 0;
			}
		}

		/* wait until process() signals more data */
		pthread_cond_wait (&data_ready, &edcast_thread_lock);
	}

 done:
	pthread_mutex_unlock (&edcast_thread_lock);
	free (framebuf);
	free (framebuf_l);
	free (framebuf_r);
	return 0;
}
	
int
process (jack_nframes_t nframes, void *arg)
{
	int chn;
	size_t i;
	int problem = 0;
	jack_thread_info_t *info = (jack_thread_info_t *) arg;

	if (!g.weareconnected) {
		return 0;
	}

	int to_write = sizeof (jack_default_audio_sample_t) * nframes;
	/* Do nothing until we're ready to begin. */
	if ((!info->can_process) || (!info->can_capture))
		return 0;

	/* copy data to ringbuffer; one per channel */
	int len;
	for (chn = 0; chn < currentChannels; chn++) {

		len = jack_ringbuffer_write_space (rb[chn]);
		if (len >= to_write) {
			len = jack_ringbuffer_write (rb[chn],
			(char *)jack_port_get_buffer (ports[chn], nframes), to_write);
			if (len < to_write) {
				printf ("ringbuffer full *, tried to write %d, but wrote %d\n", to_write, len);
				break;
			}
		}
		else {
			printf ("ringbuffer full, tried to write %d, but available %d\n", to_write, len);
			break;
		}
	}

	/* Tell the edcast thread there is work to do.  If it is already
	 * running, the lock will not be available.  We can't wait
	 * here in the process() thread, but we don't need to signal
	 * in that case, because the edcast thread will read all the
	 * data queued before waiting again. */
	if (pthread_mutex_trylock (&edcast_thread_lock) == 0) {
	    pthread_cond_signal (&data_ready);
	    pthread_mutex_unlock (&edcast_thread_lock);
	}

	return 0;
}


void
jack_shutdown (void *arg)
{
	fprintf (stderr, "JACK shutdown\n");
	// exit (0);
	abort();
}

void sigHandler(int sig) {
	jack_shutdown(NULL);
}

void
setup_edcast_thread (jack_thread_info_t *info)
{

	int short_mask;
	
	currentSamplerate = jack_get_sample_rate (info->client);
	currentChannels = info->channels;

	info->can_capture = 0;

	pthread_create (&info->thread_id, NULL, edcast_thread, info);
	pthread_create (&info->md_thread_id, NULL, edcast_metadata_thread, info);
	pthread_create (&info->reconnect_thread_id, NULL, edcast_reconnect_thread, info);
}

void
run_edcast_thread (jack_thread_info_t *info)
{
	info->can_capture = 1;
	connectToServer(&g);
	pthread_join (info->thread_id, NULL);
	if (overruns > 0) {
		fprintf (stderr,
			 "edcast failed with %ld overruns.\n", overruns);
		info->status = EPIPE;
	}
	if (info->status) {
		unlink (info->path);
	}
}

void
setup_ports (int sources, char *source_names[], jack_thread_info_t *info)
{
	unsigned int i;
	size_t in_size;
	const char **jack_ports;

	/* Allocate data structures that depend on the number of ports. */
	nports = sources;
	ports = (jack_port_t **) malloc (sizeof (jack_port_t *) * nports);
	in_size =  nports * sizeof (jack_default_audio_sample_t *);
	rb =(jack_ringbuffer_t **)malloc(sizeof (jack_ringbuffer_t *) * (sources));
	for(i=0;i<sources;i++){
		rb[i]=jack_ringbuffer_create(info->rb_size);
	}

	for (i = 0; i < nports; i++) {
		char name[64];

		sprintf (name, "in_%d", i+1);

		if ((ports[i] = jack_port_register (info->client, name, JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0)) == 0) {
			fprintf (stderr, "cannot register input port \"%s\"!\n", name);
			jack_client_close (info->client);
			exit (1);
		}
	}

	if (!getFirstTwo) {
		for (i = 0; i < nports; i++) {
			if (jack_connect (info->client, source_names[i], jack_port_name (ports[i]))) {
				fprintf (stderr, "cannot connect input port %s to %s\n", jack_port_name (ports[i]), source_names[i]);
				jack_client_close (info->client);
				exit (1);
			} 
		}
	}
	else {
		jack_ports = jack_get_ports (info->client, NULL, NULL, 0);

		int portNum = 0;
		for (i = 0; jack_ports[i]; ++i) {
			if (portNum >= 2) {
				break;
			}
			if (strstr(jack_ports[i], portMatch)) {
				jack_port_t *port = jack_port_by_name (info->client, jack_ports[i]);
				if (port) {
					int flags = jack_port_flags (port);
					if (flags & JackPortIsOutput) {
						printf("registering with %s\n", jack_ports[i]);
						if (jack_connect (info->client, jack_ports[i], jack_port_name(ports[portNum]))) {
							fprintf (stderr, "cannot connect input port %s to %s\n", jack_port_name (ports[portNum]), jack_ports[i]);
							jack_client_close (info->client);
							exit (1);
						}
						portNum++;
					}
				}
			}
		}
		if (portNum < 2) {
			printf("Could not find at least two output ports matching (%s)\n", portMatch);
			jack_client_close (info->client);
			exit (1);
		}

	}

	info->can_process = 1;		/* process() can start, now */
}

int
main (int argc, char *argv[])

{
	jack_client_t *client;
	jack_thread_info_t thread_info;
	int c;
	char	jackClientName[1024] = "";
	int ret = 0;
	struct stat buf;
	int i;

	int longopt_index = 0;
	extern int optind, opterr;
	int show_usage = 0;
	char *optstring = "p:n:c:d:f:b:B:h";
	struct option long_options[] = {
		{ "portmatch", 1, 0, 'p' },
		{ "name", 1, 0, 'n' },
		{ "config", 1, 0, 'c' },
		{ "help", 0, 0, 'h' },
		{ "duration", 1, 0, 'd' },
		{ "file", 1, 0, 'f' },
		{ "bitdepth", 1, 0, 'b' },
		{ "bufsize", 1, 0, 'B' },
		{ 0, 0, 0, 0 }
	};

	signal(SIGINT, sigHandler);

	memset (&thread_info, 0, sizeof (thread_info));
	thread_info.rb_size = DEFAULT_RB_SIZE;
	opterr = 0;


	memset(&g, '\000', sizeof(g));
	
	setServerStatusCallback(&g, serverStatusCallback);
	setGeneralStatusCallback(&g, generalStatusCallback);
	setWriteBytesCallback(&g, writeBytesCallback);

	addBasicEncoderSettings(&g);
	strcpy(jackClientName, "edcast");
	while ((c = getopt_long (argc, argv, optstring, long_options, &longopt_index)) != -1) {
		switch (c) {
		case 1:
			/* getopt signals end of '-' options */
			break;
		case 'p':
			strcpy(portMatch, optarg);
			getFirstTwo = 1;
			break;
		case 'n':
			strcpy(jackClientName, optarg);
			break;
		case 'c':
			i = stat (optarg, &buf );
			if ( i != 0 ) {
				printf("Cannot open config file (%s)\n", optarg);
				exit(1);
			}
			setConfigFileName(&g, optarg);
			readConfigFile(&g, 1);
			break;
		case 'h':
			show_usage++;
			break;
		case 'd':
			thread_info.duration = atoi (optarg);
			break;
		case 'f':
			thread_info.path = optarg;
			break;
		case 'b':
			thread_info.bitdepth = atoi (optarg);
			break;
		case 'B':
			thread_info.rb_size = atoi (optarg);
			break;
		default:
			fprintf (stderr, "error\n");
			show_usage++;
			break;
		}
	}

	if (show_usage || ((optind == argc) && (!getFirstTwo))) {
		fprintf (stderr, "usage: edcast -c configfile [ -n jack_client_name ] [ -p portmatch ] [ jackport1 [ jackport2 ... ]]\n");
		fprintf(stderr, "Where:\n");
		fprintf(stderr, "-c : config file that specified encoding settings\n");
		fprintf(stderr, "-n : name used to register with jackd\n");
		fprintf(stderr, "-p : if specified, edcast will connect to the first two output ports matching this name.\n");
		fprintf(stderr, "jackportX : explicitly specify a jack port name\n");
		exit (1);
	}



	if ((client = jack_client_new (jackClientName)) == 0) {
		fprintf (stderr, "jack server not running?\n");
		exit (1);
	}

	thread_info.client = client;
	if (getFirstTwo) {
		thread_info.channels = 2;
	}
	else {
		thread_info.channels = argc - optind;
	}
	thread_info.can_process = 0;

	setLogFlags();

	setup_edcast_thread (&thread_info);

	jack_set_process_callback (client, process, &thread_info);
	jack_on_shutdown (client, jack_shutdown, &thread_info);

	if (jack_activate (client)) {
		fprintf (stderr, "cannot activate client");
	}

	setup_ports (thread_info.channels, &argv[optind], &thread_info);

	run_edcast_thread (&thread_info);

	jack_client_close (client);

	jack_ringbuffer_free (rb[0]);
	jack_ringbuffer_free (rb[1]);

	exit (0);
}
