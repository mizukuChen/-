/*
 * @Author: mizuku 3553989549@qq.com
 * @Date: 2025-07-24 19:43:00
 * @LastEditors: mizuku 3553989549@qq.com
 * @LastEditTime: 2025-07-24 21:25:51
 * @FilePath: \MDK-ARMd:\work_office\diansai_project\bujin_moter\Core\Src\Mode_28byj48.c
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
#include <main.h>
#include <28byj48.h>

#define STEPS_PER_CIRCLE 4096
#define DEG_PER_STEP     (360.0f / STEPS_PER_CIRCLE)

static const GPIO_PinState step_sequence[8][4] = {
    {1, 0, 0, 0},
    {1, 1, 0, 0},
    {0, 1, 0, 0},
    {0, 1, 1, 0},
    {0, 0, 1, 0},
    {0, 0, 1, 1},
    {0, 0, 0, 1},
    {1, 0, 0, 1}
};

void StepMotor_Init(void) {
    // 引脚初始化已由 CubeMX 完成，此处保留接口便于扩展
}

static inline void StepMotor_WritePins_X(const GPIO_PinState value[]) {
    HAL_GPIO_WritePin(XIN1_GPIO_Port, XIN1_Pin, value[0]);
    HAL_GPIO_WritePin(XIN2_GPIO_Port, XIN2_Pin, value[1]);
    HAL_GPIO_WritePin(XIN3_GPIO_Port, XIN3_Pin, value[2]);
    HAL_GPIO_WritePin(XIN4_GPIO_Port, XIN4_Pin, value[3]);
}

static inline void StepMotor_WritePins_Y(const GPIO_PinState value[]) {
    HAL_GPIO_WritePin(YIN1_GPIO_Port, YIN1_Pin, value[0]);
    HAL_GPIO_WritePin(YIN2_GPIO_Port, YIN2_Pin, value[1]);
    HAL_GPIO_WritePin(YIN3_GPIO_Port, YIN3_Pin, value[2]);
    HAL_GPIO_WritePin(YIN4_GPIO_Port, YIN4_Pin, value[3]);
}

void StepMotor_SetSpeed(uint8_t motor_mane, int32_t step_count, uint8_t delay_time) {
    static int8_t stepX = {0};//横向步进电机状态
    static int8_t stepY = {0};//纵向步进电机状态
    
    int8_t one_step = 1;//单步移动的方向
    if(step_count < 0)
    {
        one_step = -1;
        step_count = -step_count;
    }//处理反向转动

    for (uint32_t i = 0; i < step_count; i++) {
        if(motor_mane == 0)//横向移动
        {
            StepMotor_WritePins_X(step_sequence[stepX]);
            stepX = (stepX + one_step + 8) % 8;//更新横向步进电机状态
        }
        if(motor_mane == 1)//纵向移动
        {
            StepMotor_WritePins_Y(step_sequence[stepY]);
            stepY = (stepY + one_step + 8) % 8;//更新纵向步进电机状态
        }
        //驱动步进电机

        HAL_Delay((uint32_t)delay_time); // 使用速度映射的 delay_ms
    }
}

void StepMotor_TurnAngle(uint8_t motor_mane, float angle_deg, uint8_t delay_time) {
    StepMotor_SetSpeed(motor_mane, (int32_t)((angle_deg / DEG_PER_STEP) + 0.5f), delay_time);
}

void StepMotor_TurnCircle(uint8_t motor_mane, int8_t circles, uint8_t delay_time) {
    StepMotor_SetSpeed(motor_mane, circles * STEPS_PER_CIRCLE, delay_time);
}





