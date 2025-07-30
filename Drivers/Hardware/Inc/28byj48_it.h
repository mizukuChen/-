#ifdef __28BYJ48_IT_H__
#define __28BYJ48_IT_H__

#include <main.h>  

extern char msg_vector[5];

void StepMotor_Init_IT(void);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param step_count 移动的拍数（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_SetSpeed_IT(uint8_t motor_mane, int32_t step_count, float delay_time);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param angle_deg 移动的角度（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_TurnAngle_IT(uint8_t motor_mane, float angle_deg, float delay_time);

/**
 * @brief 
 * 
 * @param motor_mane 用于选择步进电机（0：横向，1：纵向）
 * @param circles 移动的圈数（>0为向左/向上）
 * @param delay_time 每一拍的时间间隔(ms),一般填3
 */
void StepMotor_TurnCircle_IT(uint8_t motor_mane, int8_t circles, float delay_time);


#endif