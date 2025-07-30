#include <main.h>
#include <MKS42C.h>
#include <MKS42C_uart.h>


float Step42_Read_encoder_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组
    uint8_t rxBuffer[8]; // 接受数据数组
    uint16_t encode = 0;
    float angle = 0;

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0x30;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
    HAL_UART_Receive(UART, rxBuffer, 8, 50);

    encode = (uint16_t)rxBuffer[5]<<8 + (uint16_t)rxBuffer[6];
    angle = encode * 360.0 / 65536;
    return angle;
}

int32_t Step42_Read_pulses_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组
    uint8_t rxBuffer[6]; // 接受数据数组
    uint16_t pulses = 0;

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0x33;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
    HAL_UART_Receive(UART, rxBuffer, 6, 50);

    pulses = (int32_t)rxBuffer[1]<<24 + (int32_t)rxBuffer[2]<<16 + (int32_t)rxBuffer[3]<<8 + (int32_t)rxBuffer[4];
    return pulses;
}

float Step42_Read_position_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组
    uint8_t rxBuffer[6]; // 接受数据数组
    int32_t posion_encode = 0;
    float posion = 0;

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0x36;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
    HAL_UART_Receive(UART, rxBuffer, 6, 50);

    posion_encode = (int32_t)rxBuffer[1]<<24 + (int32_t)rxBuffer[2]<<16 + (int32_t)rxBuffer[3]<<8 + (int32_t)rxBuffer[4];
    posion = posion_encode * 360.0 / 65536;
    return posion;
}

float Step42_Read_error_uart(uint8_t moter_name)
{
    uint8_t txBuffer[4]; // 发送数据数组
    uint8_t rxBuffer[4]; // 接受数据数组
    int16_t error = 0;
    float error_angle = 0;

    txBuffer[0] = 0xe0 + moter_name;           // 从机地址
    txBuffer[1] = 0x39;                        // 功能码
    txBuffer[2] = Step42_getCheckSum(txBuffer, 2);    // 计算校验位
    txBuffer[3] = '\0';

    HAL_UART_Transmit(UART, txBuffer, 3, 30);
    HAL_UART_Receive(UART, rxBuffer, 4, 50);

    error = (uint16_t)rxBuffer[1]<<8 + (uint16_t)rxBuffer[2];
    error_angle = error * 360.0 / 65536;
    return error_angle;
}







