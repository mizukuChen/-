#ifndef __OLED_H
#define __OLED_H 

#include "main.h"
#include "stdlib.h"	
#include"stm32h743xx.h"

//-----------------OLED端口定义---------------- 

//#define OLED_D0_GPIO_Port OLED5_GPIO_Port
//#define OLED_D0_Pin OLED5_Pin
//#define OLED_D1_GPIO_Port OLED4_GPIO_Port
//#define OLED_D1_Pin OLED4_Pin
//#define OLED_RES_GPIO_Port OLED3_GPIO_Port
//#define OLED_RES_Pin OLED3_Pin
//#define OLED_DC_GPIO_Port OLED2_GPIO_Port
//#define OLED_DC_Pin OLED2_Pin
//#define OLED_CS_GPIO_Port OLED1_GPIO_Port
//#define OLED_CS_Pin OLED1_Pin
#define RESET 0
#define SET 1

//此处改成自己设定的端口
//无需使用MX自带SPI，直接设置端口为推挽输出，引脚默认高电平即可
//使用：
//include "oled.h"即可，不要再include "oledfont.h"
//首先Init，使用ShowString等函数后须调用Refresh函数，否则不会显示

#define OLED_SCL_Clr() HAL_GPIO_WritePin(OLED_D0_GPIO_Port, OLED_D0_Pin, RESET)//SCL，连接D0
#define OLED_SCL_Set() HAL_GPIO_WritePin(OLED_D0_GPIO_Port, OLED_D0_Pin, SET)

#define OLED_SDA_Clr() HAL_GPIO_WritePin(OLED_D1_GPIO_Port, OLED_D1_Pin, RESET)//SDA，连接D1
#define OLED_SDA_Set() HAL_GPIO_WritePin(OLED_D1_GPIO_Port, OLED_D1_Pin, SET)

#define OLED_RES_Clr() HAL_GPIO_WritePin(OLED_RES_GPIO_Port, OLED_RES_Pin, RESET)//RES
#define OLED_RES_Set() HAL_GPIO_WritePin(OLED_RES_GPIO_Port, OLED_RES_Pin, SET)

#define OLED_DC_Clr()  HAL_GPIO_WritePin(OLED_DC_GPIO_Port, OLED_DC_Pin, RESET)//DC
#define OLED_DC_Set()  HAL_GPIO_WritePin(OLED_DC_GPIO_Port, OLED_DC_Pin, SET)

#define OLED_CS_Clr()  HAL_GPIO_WritePin(OLED_CS_GPIO_Port, OLED_CS_Pin, RESET)//CS
#define OLED_CS_Set()  HAL_GPIO_WritePin(OLED_CS_GPIO_Port, OLED_CS_Pin, SET)

#define u8 uint8_t
#define u16 uint16_t
#define u32 uint32_t

#define OLED_CMD  0	//写命令
#define OLED_DATA 1	//写数据

void OLED_ClearPoint(u8 x,u8 y);
void OLED_ColorTurn(u8 i);
void OLED_DisplayTurn(u8 i);
void OLED_WR_Byte(u8 dat,u8 mode);
void OLED_DisPlay_On(void);
void OLED_DisPlay_Off(void);
void OLED_Refresh(void);
void OLED_Clear(void);
void OLED_Interval_On(void);
void OLED_Dot_All_On(void);
void OLED_DrawPoint(u8 x,u8 y,u8 t);
void OLED_DrawLine(u8 x1,u8 y1,u8 x2,u8 y2,u8 mode);
void OLED_DrawCircle(u8 x,u8 y,u8 r);
void OLED_ShowChar(u8 x,u8 y,u8 chr,u8 size1,u8 mode);
void OLED_ShowChar6x8(u8 x,u8 y,u8 chr,u8 mode);
void OLED_ShowString(u8 x,u8 y,u8 *chr,u8 size1,u8 mode);
void OLED_ShowNum(u8 x,u8 y,u32 num,u8 len,u8 size1,u8 mode);
void OLED_ShowChinese(u8 x,u8 y,u8 num,u8 size1,u8 mode);
void OLED_ScrollDisplay(u8 num,u8 space,u8 mode);
void OLED_ShowPicture(u8 x,u8 y,u8 sizex,u8 sizey,u8 BMP[],u8 mode);
void OLED_Init(void);

#endif

