#include <main.h>
#include <MKS42C.h>
#include <MKS42C_uart.h>


void Step42_speedMode_uart(uint8_t moter_name, uint8_t dir, uint8_t speed)
{
    uint8_t txBuffer[5]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xf6;                        // 功能码
    txBuffer[2] = (dir << 7) | (speed & 0x7F); // 方向和速度低7位
    txBuffer[3] = Step42_getCheckSum(txBuffer, 3);    // 计算校验位
    txBuffer[4] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 4, 30);
}

void Step42_positionMode_uart(uint8_t moter_name, uint8_t speed, float angle)
{
    uint8_t txBuffer[9]; // 发送数据数组
    uint32_t pulses;//脉冲数
    uint8_t dir = 1;//移动方向

    if(angle > 0){
        dir = 1;
    }
    else if(angle < 0){
        dir = -1;
        angle = -angle;
    }
    pulses = angle * STEP_MODE / ANGLE_MODE;

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xfd;                        // 功能码
    txBuffer[2] = (dir << 7) | (speed & 0x7F); // 方向和速度低7位
    txBuffer[3] = (pulses >> 24)&0xFF;  //脉冲数 bit31 - bit24
    txBuffer[4] = (pulses >> 16)&0xFF;  //脉冲数 bit23 - bit16
    txBuffer[5] = (pulses >> 8)&0xFF;   //脉冲数 bit15 - bit8
    txBuffer[6] = (pulses >> 0)&0xFF;   //脉冲数 bit7 - bit0
    txBuffer[7] = Step42_getCheckSum(txBuffer, 7);    // 计算校验位
    txBuffer[8] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 8, 30);
}

void Step42_Stop_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xf7;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_Enable_uart(uint8_t moter_name, uint8_t status)
{
    uint8_t txBuffer[5]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xf3;                        // 功能码
    txBuffer[2] = status;                        // 使能状态
    txBuffer[3] = Step42_getCheckSum(txBuffer, 3);    // 计算校验位
    txBuffer[4] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_save_speed_uart(uint8_t moter_name)
{
    uint8_t txBuffer[5]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xff;                        // 功能码
    txBuffer[2] = 0xc8;                        // 使能状态
    txBuffer[3] = Step42_getCheckSum(txBuffer, 3);    // 计算校验位
    txBuffer[4] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}

void Step42_clear_speed_uart(uint8_t moter_name)
{
    uint8_t txBuffer[5]; // 发送数据数组

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0xff;                        // 功能码
    txBuffer[2] = 0xca;                        // 使能状态
    txBuffer[3] = Step42_getCheckSum(txBuffer, 3);    // 计算校验位
    txBuffer[4] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
}














