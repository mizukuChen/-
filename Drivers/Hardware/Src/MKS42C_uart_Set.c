#include <main.h>
#include <MKS42C.h>
#include <MKS42C_uart.h>


void Step42_reset_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0x3f;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Set_Kp_uart(uint8_t moter_name, uint16_t Kp)
{
    uint8_t txBuffer[6]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xa1;                        // 功能码
    txBuffer[2] = (Kp >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[3] = (Kp >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[4] = Step42_getCheckSum(txBuffer, 4);    // 计算校验位
    txBuffer[5] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Set_Ki_uart(uint8_t moter_name, uint16_t Ki)
{
    uint8_t txBuffer[6]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xa2;                        // 功能码
    txBuffer[2] = (Ki >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[3] = (Ki >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[4] = Step42_getCheckSum(txBuffer, 4);    // 计算校验位
    txBuffer[5] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Set_Kd_uart(uint8_t moter_name, uint16_t Kd)
{
    uint8_t txBuffer[6]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xa3;                        // 功能码
    txBuffer[2] = (Kd >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[3] = (Kd >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[4] = Step42_getCheckSum(txBuffer, 4);    // 计算校验位
    txBuffer[5] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Set_acc_uart(uint8_t moter_name, uint16_t acc)
{
    uint8_t txBuffer[6]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xa4;                        // 功能码
    txBuffer[2] = (acc >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[3] = (acc >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[4] = Step42_getCheckSum(txBuffer, 4);    // 计算校验位
    txBuffer[5] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Set_MaxT_uart(uint8_t moter_name, uint16_t MaxT)
{
    uint8_t txBuffer[6]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xa5;                        // 功能码
    txBuffer[2] = (MaxT >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[3] = (MaxT >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[4] = Step42_getCheckSum(txBuffer, 4);    // 计算校验位
    txBuffer[5] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}