#ifndef __MKS42C_IT_H__
#define __MKS42C_IT_H__

#include <main.h>

void Step42_Init_IT(void);
void Step42_Stp_IT(uint8_t motor_mane, int32_t step_count, uint8_t fps);

#endif
