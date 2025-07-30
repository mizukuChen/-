#include <main.h>
#include <MKS42C.h>
#include <MKS42C_uart.h>


uint8_t Step42_getCheckSum(uint8_t *buffer, uint8_t size)
{
    uint8_t sum = 0;
    for (uint8_t i = 0; i < size; i++)
    {
        sum += buffer[i]; // 计算累加值
    }
    return sum; // 返回校验和
}

bool Step42_waitingForACK(uint8_t len)
{
    uint8_t rxBuffer[20]; // 接收数据数组
    uint8_t rxCnt = 0;    // 接收数据计数
    bool retVal = 0; // 返回值
    unsigned long sTime;      // 计时起始时刻
    unsigned long time;       // 当前时刻
    uint8_t rxByte;

    sTime = HAL_GetTick(); // 获取当前时刻
    rxCnt = 0;        // 接收计数值置0
    HAL_UART_Receive_IT(&huart3, rxBuffer, len);
    return (retVal);
}