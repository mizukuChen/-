#include <main.h>
#include <MKS42C.h>
#include <MKS42C_it.h>

//目标向量的一般大小
#define NORMAL_VECTOR 48.33
//帧率的一般大小（单位：kHz）
#define NORMAL_FPS 100
//像素与脉冲延时的乘积（单位：Us）
#define VECTOR_PLUS_DELAY 1000 * NORMAL_VECTOR / NORMAL_FPS
//单个像素对应的步数差
#define VECTOR_TO_STEP 0.3

#define STEPX_TIM &htim16
#define STEPY_TIM &htim17

int16_t vectorX = 0, vectorY = 0;//接受向量信息  
static int32_t remain_stepX = 0;//横向步进电机剩余移动步数
static int32_t remain_stepY = 0;//纵向步进电机剩余移动步数
char msg_vector[5] = {0};//用于接收坐标信息

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
    static uint16_t sum = 0;
    if(huart == &huart3){
        vectorX = *(int16_t*)msg_vector;
        vectorY = *(int16_t*)(msg_vector+2);
        char data[20] = {0};
        sprintf(data, "%d %d %d", vectorX, vectorY, sum);
        OLED_ShowString(0, 10, data, 8, 1);
        OLED_ShowString(0, 20, "now in loop", 8, 1);
        OLED_ShowString(0, 30, msg_vector, 8, 1);
        OLED_Refresh();
        //memset(msgdata, 0, 2);
        //memset(&receive_x, 0, 2);
        //memset(&receive_y, 0, 2);
        __HAL_TIM_SET_AUTORELOAD(STEPX_TIM, VECTOR_PLUS_DELAY / vectorX);
        __HAL_TIM_SET_AUTORELOAD(STEPY_TIM, VECTOR_PLUS_DELAY / vectorY);
        remain_stepX = vectorX * VECTOR_TO_STEP;
        remain_stepY = vectorY * VECTOR_TO_STEP;
        sum++;
        HAL_UART_Receive_IT(&huart3, msg_vector, 4);
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if(htim == STEPX_TIM)//控制横向步进电机
    {
        if(remain_stepX--)
        {
            HAL_GPIO_TogglePin(StpX_GPIO_Port, StpX_Pin);
        }
    }
    if(htim == STEPY_TIM)//控制纵向步进电机
    {
        if(remain_stepX--)
        {
            HAL_GPIO_TogglePin(StpY_GPIO_Port, StpY_Pin);
        }
    }   
}

void Step42_Init_IT(void) {
    HAL_TIM_Base_Start_IT(STEPX_TIM);
    HAL_TIM_Base_Start_IT(STEPY_TIM);
    HAL_GPIO_WritePin(StpX_GPIO_Port, StpX_Pin, 0);
    HAL_GPIO_WritePin(StpY_GPIO_Port, StpY_Pin, 0);
}

void Step42_Stp_IT(uint8_t motor_mane, int32_t step, uint8_t fps){
    if(step > 0)
    {
        Step42_Dir(motor_mane, TURN_FORWARD);
    }

    else if(step < 0)
    {
        Step42_Dir(motor_mane, TURN_REVERSE);
        step = -step;
    }

    uint16_t delay_time = 1000 / fps;

    if(motor_mane == 0){
        __HAL_TIM_SET_AUTORELOAD(STEPX_TIM, delay_time * 0.5);
        remain_stepX = step * 2;
    }

    if(motor_mane == 1){
        __HAL_TIM_SET_AUTORELOAD(STEPY_TIM, delay_time * 0.5);
        remain_stepY = step * 2;
    }
}

void Step42_TurnAngle_IT(uint8_t motor_mane, float angle_deg, uint8_t fps) {
    if(angle_deg > 0)
    {
        Step42_Dir(motor_mane, TURN_FORWARD);
    }

    else if(angle_deg < 0)
    {
        Step42_Dir(motor_mane, TURN_REVERSE);
    }

    Step42_Stp_IT(motor_mane, (int32_t)((angle_deg / DEG_PER_STEP) + 0.5f), fps);
}

void StepMotor_TurnCircle_IT(uint8_t motor_mane, int8_t circles, uint8_t fps) {
    if(circles > 0)
    {
        Step42_Dir(motor_mane, TURN_FORWARD);
    }

    else if(circles < 0)
    {
        Step42_Dir(motor_mane, TURN_REVERSE);
    }

    Step42_Stp_IT(motor_mane, circles * STEPS_PER_CIRCLE, fps);
}



















