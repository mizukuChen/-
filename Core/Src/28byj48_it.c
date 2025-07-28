#include <main.h>
#include <28byj48_it.h>

#define NORMAL_VECTOP 48.33
//目标向量的一般大小
#define STEPTIME_PLUS_VECTOR 10000 * 3 * NORMAL_VECTOP
//单拍间隔与坐标差的乘积
#define VECTOR_TO_STEP 0.3
//单个像素对应的步数差
#define STEPS_PER_CIRCLE 4096
#define DEG_PER_STEP     (360.0f / STEPS_PER_CIRCLE)

int16_t vectorX = 0, vectorY = 0;//接受向量信息  
static int32_t remain_stepX = 0;//横向步进电机剩余移动步数
static int32_t remain_stepY = 0;//纵向步进电机剩余移动步数
static const GPIO_PinState step_stop[4] = {0, 0, 0, 0};
//步进电机的停止状态
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
//步进电机各拍状态

void StepMotor_Init_IT(void) {
    HAL_TIM_Base_Start_IT(&htim16);
    HAL_TIM_Base_Start_IT(&htim17);
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

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
    static char msgdata[5] = {0};
    if(huart == &huart3){
        HAL_UART_Receive(&huart3, msgdata, 4, HAL_MAX_DELAY);
        vectorX = *(int16_t*)msgdata;
        vectorY = *(int16_t*)(msgdata+2);
        char data[20] = {0};
        sprintf(data, "%d %d", vectorX, vectorY);
        OLED_ShowString(0, 10, data, 8, 1);
        OLED_ShowString(0, 20, "now in loop", 8, 1);
        OLED_Refresh();
        //memset(msgdata, 0, 2);
        //memset(&receive_x, 0, 2);
        //memset(&receive_y, 0, 2);
        __HAL_TIM_SET_AUTORELOAD(&htim16, STEPTIME_PLUS_VECTOR / vectorX);
        __HAL_TIM_SET_AUTORELOAD(&htim17, STEPTIME_PLUS_VECTOR / vectorY);
        remain_stepX = vectorX * VECTOR_TO_STEP;
        remain_stepY = vectorY * VECTOR_TO_STEP;
        HAL_UART_Receive_DMA(&huart3, msgdata, 4);
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    static uint8_t stepX = 0;//横向步进电机状态
    static uint8_t stepY = 0;//纵向步进电机状态
    //char msg[15] = {0};

    if(htim == &htim16)//控制横向步进电机
    {
        if(remain_stepX > 0)
        {
            //sprintf(msg, "%d\n", remain_stepX);
            //HAL_UART_Transmit_IT(&huart1, msg, sizeof(msg));
            remain_stepX--;
            StepMotor_WritePins_X(step_sequence[stepX]);
            stepX = (stepX + 1) % 8;
        }
        else if(remain_stepX < 0)
        {
            remain_stepX++;
            StepMotor_WritePins_X(step_sequence[stepX]);
            stepX = (stepX + 7) % 8;
        }
        else if(remain_stepX == 0)
        {
            StepMotor_WritePins_X(step_stop);
        }
    }

    if(htim == &htim17)//控制纵向步进电机
    {
        if(remain_stepY > 0)
        {
            //sprintf(msg, "%d\n", remain_stepY);
            //HAL_UART_Transmit(&huart1, msg, sizeof(msg),30);
            remain_stepY--;
            StepMotor_WritePins_Y(step_sequence[stepY]);
            stepY = (stepY + 1) % 8;
        }
        else if(remain_stepY < 0)
        {
            remain_stepY++;
            StepMotor_WritePins_Y(step_sequence[stepY]);
            stepY = (stepY + 7) % 8;
        }
        else if(remain_stepY == 0)
        {
            StepMotor_WritePins_Y(step_stop);
        }
    }
}

void StepMotor_SetSpeed_IT(uint8_t motor_mane, int32_t step_count, uint8_t delay_time){
    if(motor_mane == 0){
        __HAL_TIM_SET_AUTORELOAD(&htim16, delay_time * 1000);
        remain_stepX = step_count;
    }
    if(motor_mane == 1){
        __HAL_TIM_SET_AUTORELOAD(&htim17, delay_time * 1000);
        remain_stepY = step_count;
    }
}

void StepMotor_RotateAngle_IT(uint8_t motor_mane, float angle_deg, uint8_t delay_time) {
    StepMotor_SetSpeed_IT(motor_mane, (int32_t)((angle_deg / DEG_PER_STEP) + 0.5f), delay_time);
}

void StepMotor_RotateCircle_IT(uint8_t motor_mane, int8_t circles, uint8_t delay_time) {
    StepMotor_SetSpeed_IT(motor_mane, circles * STEPS_PER_CIRCLE, delay_time);
}









