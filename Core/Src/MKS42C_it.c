#include <main.h>
#include <MKS42C_it.h>

//步数与角度对应关系
#define ANGLE_MODE 1.8
#define STEP_MODE 16
#define STEPS_PER_CIRCLE 360 / ANGLE_MODE * STEP_MODE
#define DEG_PER_STEP  1.0f / ANGLE_MODE * STEP_MODE

#define STEPX_TIM &htim16
#define STEPY_TIM &htim17

static int32_t remain_stepX = 0;//横向步进电机剩余移动步数
static int32_t remain_stepY = 0;//纵向步进电机剩余移动步数

void Step42_Init_IT(void) {
    HAL_TIM_Base_Start_IT(STEPX_TIM);
    HAL_TIM_Base_Start_IT(STEPY_TIM);
    HAL_GPIO_WritePin(StpX_GPIO_Port, StpX_Pin, 0);
    HAL_GPIO_WritePin(StpY_GPIO_Port, StpY_Pin, 0);
}

void Step42_Stp_IT(uint8_t motor_mane, int32_t step_count, uint8_t fps){
    uint16_t delay_time = 1000 / fps;
    if(motor_mane == 0){
        __HAL_TIM_SET_AUTORELOAD(STEPX_TIM, delay_time * 0.5);
        remain_stepX = step_count * 2;
    }
    if(motor_mane == 1){
        __HAL_TIM_SET_AUTORELOAD(STEPY_TIM, delay_time * 0.5);
        remain_stepY = step_count * 2;
    }
}

void Step42_TurnAngle_IT(uint8_t motor_mane, float angle_deg, uint8_t fps) {
    Step42_Stp_IT(motor_mane, (int32_t)((angle_deg / DEG_PER_STEP) + 0.5f), fps);
}

void StepMotor_TurnCircle_IT(uint8_t motor_mane, int8_t circles, uint8_t fps) {
    Step42_Stp_IT(motor_mane, circles * STEPS_PER_CIRCLE, fps);
}



















