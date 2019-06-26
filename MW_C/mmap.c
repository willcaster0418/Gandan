#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include "mmap.h"

static int
get_que_info(char *buf, char **que_name, int *rp, int *wp)
{
	char *buf_ptr;
	*que_name = (char *)malloc(3);

	buf_ptr = buf;
	memcpy(*que_name, buf_ptr, 3);
	buf_ptr = buf_ptr + 3;
	memcpy(rp, buf_ptr, sizeof(int));
	buf_ptr = buf_ptr + sizeof(int);
	memcpy(wp, buf_ptr, sizeof(int));
	buf_ptr = buf_ptr + sizeof(int);
}

static int
_get_que_info(char *buf, char **que_name, int *rp, int *wp)
{
	get_que_info(buf, que_name, rp, wp);
}

static int
add(char *buf, char op, int idx)
{
	int *ptr;
	if (op == 'r') ptr = (int *)(buf+3);
	if (op == 'w') ptr = (int *)(buf+7);
	
	*ptr = *ptr + idx;
}

static int
readp(char *buf, char **ptr, int *len)
{
	char **que_name;
	int rp, wp;
	get_que_info(buf, que_name, &rp, &wp); 
	if( (wp - rp) > 0 ) {
		*len = (wp - rp)*ITEM_SIZE;
		*ptr = buf + (rp % ITEM_MAX) * ITEM_SIZE + 3 + 2*sizeof(int);
		printf("data : %.*s\n", 10, *ptr);
		printf("data : %.*s\n", 10, *ptr);
		return 0;
	}
	return -1;
}

int 
main(int argc, char **argv)
{
	int fd;
	char *file = NULL;
	struct stat sb;
	int flag = PROT_WRITE | PROT_READ;

	if (argc < 2) 
		fprintf(stderr, "Usage: input\n");

	if ((fd = open(argv[1], O_RDWR|O_CREAT)) < 0) 
		perror("File Open Error");

	if (fstat(fd, &sb) < 0) 
		perror("fstat error");

	file = (char *)malloc((long long) sb.st_size);

	if ((file = (char *) mmap(0, sb.st_size, flag, MAP_SHARED, fd, 0)) < 0)
	{
		perror("mmap error");
		exit(1);
	}

	char *que_name;
	int rp, wp;
	_get_que_info(file, &que_name, &rp, &wp);
	printf("%d, %s, %d, %d\n", sb.st_size, que_name, rp, wp);

	int len;
	char *ptr;
	readp(file, &ptr, &len);
	printf("\n%d\n", len);
	//munmap((void *)file, sb.st_size);
	//close(fd);
	return 0;
}
