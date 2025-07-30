#ifndef __MKS42C_UART_H__
#define __MKS42C_UART_H__

#include <main.h>

#define UART &huart3

/*运动控制模块*/

/**
 * @brief 设置步进电机为速度模式
 * 
 * @param moter_name 电机名
 * @param dir 转动方向
 * @param speed 转动速度(0-127)
 */
void Step42_speedMode_uart(uint8_t moter_name, uint8_t dir, uint8_t speed);

/**
 * @brief 设置步进电机为位置模式
 * 
 * @param moter_name 电机名
 * @param speed 转动速度(0-127)
 * @param angle 转动角度(可正可负)
 */
void Step42_positionMode_uart(uint8_t moter_name, uint8_t speed, float angle);

/**
 * @brief 停止步进电机转动
 * 
 * @param moter_name 电机名
 */
void Step42_Stop_uart(uint8_t moter_name);

/**
 * @brief 使能步进电机
 * 
 * @param moter_name 电机名
 * @param status 是否使能
 */
void Step42_Enable_uart(uint8_t moter_name, uint8_t status);

/**
 * @brief 保存步进电机运动速度
 * 
 * @param moter_name 电机名
 */
void Step42_save_speed_uart(uint8_t moter_name);

/**
 * @brief 清除保存的步进电机速度
 * 
 * @param moter_name 电机名
 */
void Step42_clear_speed_uart(uint8_t moter_name);



/*参数设置模块*/

/**
 * @brief 复位步进电机
 * 
 * @param moter_name 电机名
 */
void Step42_reset_uart(uint8_t moter_name);

/**
 * @brief 设置步进电机Kp值
 * 
 * @param moter_name 电机名
 * @param Kp Kp值
 */
void Step42_Set_Kp_uart(uint8_t moter_name, uint16_t Kp);

/**
 * @brief 设置步进电机Ki值
 * 
 * @param moter_name 电机名
 * @param Ki Ki值
 */
void Step42_Set_Ki_uart(uint8_t moter_name, uint16_t Ki);

/**
 * @brief 设置步进电机Kd值
 * 
 * @param moter_name 电机名
 * @param Kd Kd值
 */
void Step42_Set_Kd_uart(uint8_t moter_name, uint16_t Kd);

/**
 * @brief 设置步进电机加速度
 * 
 * @param moter_name 电机名
 * @param acc 加速度值
 */
void Step42_Set_acc_uart(uint8_t moter_name, uint16_t acc);

/**
 * @brief 设置步进电机最大扭矩
 * 
 * @param moter_name 电机名
 * @param MaxT 最大扭矩值
 */
void Step42_Set_MaxT_uart(uint8_t moter_name, uint16_t MaxT);



/*参数读取模块*/

/**
 * @brief 阅读编码器值
 * 
 * @param moter_name 电机名
 * @return float 当前角度值
 */
float Step42_Read_encoder_uart(uint8_t moter_name);

/**
 * @brief 阅读脉冲数
 * 
 * @param moter_name 电机名
 * @return int32_t 上电后累计脉冲数
 */
int32_t Step42_Read_pulses_uart(uint8_t moter_name);

/**
 * @brief 阅读位置信息
 * 
 * @param moter_name 电机名
 * @return float 自上电/使能起所转过的角度
 */
float Step42_Read_position_uart(uint8_t moter_name);

/**
 * @brief 阅读误差值
 * 
 * @param moter_name 电机名
 * @return float 位置角度误差
 */
float Step42_Read_error_uart(uint8_t moter_name);



/*通讯模块*/
uint8_t Step42_getCheckSum(uint8_t *buffer, uint8_t size);
bool Step42_waitingForACK(uint8_t len);

#endif
