#include <main.h>
#include <MKS42C.h>

void Step42_Init(void) {
    HAL_GPIO_WritePin(StpX_GPIO_Port, StpX_Pin, 0);
    HAL_GPIO_WritePin(StpY_GPIO_Port, StpY_Pin, 0);
}

void Step42_En(uint8_t motor_mane, GPIO_PinState status)
{
    if(motor_mane == 0){
        HAL_GPIO_WritePin(EnX_GPIO_Port, EnX_Pin, status);
    }
	if(motor_mane == 1){
        HAL_GPIO_WritePin(EnY_GPIO_Port, EnY_Pin, status);
    }
}

void Step42_Dir(uint8_t motor_mane, GPIO_PinState status)
{
	if(motor_mane == 0){
        HAL_GPIO_WritePin(DirX_GPIO_Port, DirX_Pin, status);
    }
	if(motor_mane == 1){
        HAL_GPIO_WritePin(DirY_GPIO_Port, DirY_Pin, status);
    }
}

void Step42_Stp(uint8_t motor_mane, uint32_t step, uint8_t fps)
{
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

	if(motor_mane == 0)
    {
        while(step--)
        {
            HAL_GPIO_WritePin(StpX_GPIO_Port, StpX_Pin, 1);
            Delay_Us(0.5 * delay_time);
		    HAL_GPIO_WritePin(StpX_GPIO_Port, StpX_Pin, 0);
		    Delay_Us(0.5 * delay_time);
        }
    }

	if(motor_mane == 1)
    {
        while(step--)
        {
            HAL_GPIO_WritePin(StpY_GPIO_Port, StpY_Pin, 1);
            Delay_Us(0.5 * delay_time);
		    HAL_GPIO_WritePin(StpY_GPIO_Port, StpY_Pin, 0);
		    Delay_Us(0.5 * delay_time);    
        }
    }
}

void Step42_TurnAngle(uint8_t motor_mane, float angle_deg, uint8_t fps) {
    if(angle_deg > 0)
    {
        Step42_Dir(motor_mane, TURN_FORWARD);
    }
    
    else if(angle_deg < 0)
    {
        Step42_Dir(motor_mane, TURN_REVERSE);
    }

    Step42_Stp(motor_mane, (int32_t)((angle_deg / DEG_PER_STEP) + 0.5f), fps);
}

void StepMotor_TurnCircle(uint8_t motor_mane, int8_t circles, uint8_t fps) {
    if(circles > 0)
    {
        Step42_Dir(motor_mane, TURN_FORWARD);
    }

    else if(circles < 0)
    {
        Step42_Dir(motor_mane, TURN_REVERSE);
    }

    Step42_Stp(motor_mane, circles * STEPS_PER_CIRCLE, fps);
}





















