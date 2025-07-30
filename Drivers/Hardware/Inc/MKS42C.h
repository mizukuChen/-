#ifndef __MKS42C_H__
#define __MKS42C_H__

#include <main.h>

//步数与角度对应关系
#define ANGLE_MODE 1.8
#define STEP_MODE 16
#define STEPS_PER_CIRCLE 360 / ANGLE_MODE * STEP_MODE
#define DEG_PER_STEP  1.0f / ANGLE_MODE * STEP_MODE
#define TURN_FORWARD 1
#define TURN_REVERSE 0

void Step42_Init(void);
void Step42_En(uint8_t motor_mane, GPIO_PinState status);
void Step42_Dir(uint8_t motor_mane, GPIO_PinState status);
void Step42_Stp(uint8_t motor_mane, uint32_t steps,uint8_t fps);
void Step42_TurnAngle(uint8_t motor_mane, float angle_deg, uint8_t fps);
void StepMotor_TurnCircle(uint8_t motor_mane, int8_t circles, uint8_t fps);

#endif
