#include <stdio.h>
#include <string.h>

void main(){
    //short t = 5423;
    //unsigned char * p = &t;
    //unsigned char msg[2] = {0};
    //msg[0] = *p;
    //msg[1] = *(p+1); 
    //short i = ((short)msg[0]<<8 +(short)msg[1]);
    //printf("%d %d\n",msg[0],msg[1]);
    //printf("%d",i);
    //scanf("%d",i);

    short length = -5638;
    char *p = (char*)&length;
    char send_buf[100];

    memcpy(send_buf, p, sizeof(short));

    // 解包时，取前4个字节为包长
    short receive = *(short*)send_buf;
    char msgdata[20] = {0};
    sprintf(msgdata, "%d", receive);
    printf("%s",msgdata);
}