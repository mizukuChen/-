#ifndef __28BYJ48_H__
#define __28BYJ48_H__

#include <main.h>

void StepMotor_Init(void);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param step_count 移动的拍数（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_SetSpeed(uint8_t motor_mane, int32_t step_count, uint8_t delay_time);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param angle_deg 移动的角度（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_RotateAngle(uint8_t motor_mane, float angle_deg, uint8_t delay_time);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param circles 移动的圈数（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_RotateCircle(uint8_t motor_mane, int8_t circles, uint8_t delay_time);

#endif