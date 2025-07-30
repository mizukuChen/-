// pid模组

/**
 * @file    Mode_pid.c
 * @version v1.3
 * @author  Bairu
 * @date    2024��8��21�� 16:09:44
 * @brief   PID�㷨(λ��ʽ������ʽ)
 */

 #include <main.h>
#include <Mode_pid.h>

/**
 * @brief  λ��ʽPID������ʼ��
 * @param  pid PID�����ṹ��
 * @param  Kp ������ϵ��
 * @param  Ki ������ϵ��
 * @param  Kd ΢����ϵ��
 * @param  target Ŀ��ֵ
 * @param  minIntegral �����޷�-��Сֵ
 * @param  maxIntegral �����޷�-���ֵ
 * @param  minOutput PID����޷�-��Сֵ
 * @param  maxOutput PID����޷�-���ֵ
 * @retval ��
 */
void PID_Init(PID *pid, float Kp, float Ki, float Kd, float target,
              float minIntegral, float maxIntegral,
              float minOutput, float maxOutput)
{
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
    pid->target = target;
    pid->minIntegral = minIntegral;
    pid->maxIntegral = maxIntegral;
    pid->minOutput = minOutput;
    pid->maxOutput = maxOutput;
    pid->error = 0.0;
    pid->last_error = 0.0;
    pid->integral = 0.0;
}

/**
 * @brief  ����λ��ʽPIDĿ��ֵ
 * @param  pid PID�����ṹ��
 * @param  target Ŀ��ֵ
 * @retval ��
 */
void PID_ResetTarget(PID *pid, float target)
{
    pid->target = target;
}

/**
 * @brief  ����λ��ʽPID����ϵ��
 * @param  pid PID�����ṹ��
 * @param  K_x Ҫ�޸ĵ�ϵ��
 *      @arg ��Чȡֵ:
 *          - \b K_p : p��ϵ��
 *          - \b K_i : i��ϵ��
 *          - \b K_d : d��ϵ��
 * @param  value ϵ������ֵ
 * @retval ��
 */
void PID_Reset_pid(PID *pid, uint8_t K_x, float value)
{
    switch (K_x)
    {
    case K_p:
        pid->Kp = value;
        break;
    case K_i:
        pid->Ki = value;
        break;
    case K_d:
        pid->Kd = value;
        break;
    }
}

/**
 * @brief  λ��ʽPID���㡣
 * @param  pid PID�����ṹ��
 * @param  input ��ǰֵ
 * @retval λ��ʽPID������
 */
float PID_Compute(PID *pid, float input)
{
    pid->error = pid->target - input;                        // �������
    pid->integral += pid->error;                             // �ۻ����
    float p_term = pid->Kp * pid->error;                     // ������
    float i_term = pid->Ki * pid->integral;                  // ������
    float d_term = pid->Kd * (pid->error - pid->last_error); // ΢����

    // �����޷�
    if (i_term > pid->maxIntegral)
        i_term = pid->maxIntegral;
    else if (i_term < pid->minIntegral)
        i_term = pid->minIntegral;

    // �����ϴ����
    pid->last_error = pid->error;

    float PID_Output = p_term + i_term + d_term;

    // PID����޷�
    if (PID_Output > pid->maxOutput)
        PID_Output = pid->maxOutput;
    else if (PID_Output < pid->minOutput)
        PID_Output = pid->minOutput;

    return PID_Output;
}

float PID_Compute_reverse(PID *pid, float input, float Kp)
{
    pid->error = pid->target - input;                        // �������
    pid->integral += pid->error;                             // �ۻ����
    /* if(pid->last_error == 0 || pid->error == 0){
        pid->Kd = Kp;
    }
    else if(pid->error / pid->last_error > 0){
        pid->Kd = -pid->Kd;
    } */
    float p_term = pid->Kp * pid->error;                     // ������
    float i_term = pid->Ki * pid->integral;                  // ������
    float d_term = pid->Kd * (pid->error - pid->last_error); // ΢����

    // �����޷�
    if (i_term > pid->maxIntegral)
        i_term = pid->maxIntegral;
    else if (i_term < pid->minIntegral)
        i_term = pid->minIntegral;

    // �����ϴ����
    pid->last_error = pid->error;

    float PID_Output = p_term + i_term + d_term;

    // PID����޷�
    if (PID_Output > pid->maxOutput)
        PID_Output = pid->maxOutput;
    else if (PID_Output < pid->minOutput)
        PID_Output = pid->minOutput;

    return PID_Output;
}

/**
 * @brief  ����ʽPID������ʼ��
 * @param  incpid PID�����ṹ��
 * @param  Kp ������ϵ��
 * @param  Ki ������ϵ��
 * @param  Kd ΢����ϵ��
 * @param  target Ŀ��ֵ
 * @param  minOutput PID����޷�-��Сֵ
 * @param  maxOutput PID����޷�-���ֵ
 * @retval ��
 */
void IncPID_Init(IncPID *incpid, float Kp, float Ki, float Kd, float target,
                 float minOutput, float maxOutput)
{
    incpid->Kp = Kp;
    incpid->Ki = Ki;
    incpid->Kd = Kd;
    incpid->target = target;
    incpid->minOutput = minOutput;
    incpid->maxOutput = maxOutput;
    incpid->error = 0.0;
    incpid->last_error = 0.0;
    incpid->prev_error = 0.0;
    incpid->IncPID_Output = 0.0;
}

/**
 * @brief  ��������ʽPIDĿ��ֵ
 * @param  incpid PID�����ṹ��
 * @param  target Ŀ��ֵ
 * @retval ��
 */
void IncPID_ResetTarget(IncPID *incpid, float target)
{
    incpid->target = target;
}

/**
 * @brief  ��������ʽPID����ϵ��
 * @param  pid PID�����ṹ��
 * @param  K_x Ҫ�޸ĵ�ϵ��
 *      @arg ��Чȡֵ:
 *          - \b K_p : p��ϵ��
 *          - \b K_i : i��ϵ��
 *          - \b K_d : d��ϵ��
 * @param  value ϵ������ֵ
 * @retval ��
 */
void IncPID_Reset_pid(IncPID *incpid, uint8_t K_x, float value)
{
    switch (K_x)
    {
    case K_p:
        incpid->Kp = value;
        break;
    case K_i:
        incpid->Ki = value;
        break;
    case K_d:
        incpid->Kd = value;
        break;
    }
}

/**
 * @brief  ����ʽPID���㡣
 * @param  incpid PID�����ṹ��
 * @param  input ��ǰֵ
 * @retval ����ʽPID������
 */
float IncPID_Compute(IncPID *incpid, float input)
{
    incpid->error = incpid->target - input;

    float p_term = incpid->Kp * (incpid->error - incpid->last_error);                          // ������
    float i_term = incpid->Ki * incpid->error;                                                 // ������
    float d_term = incpid->Kd * (incpid->error - 2 * incpid->last_error + incpid->prev_error); // ΢����

    // �������
    incpid->prev_error = incpid->last_error;
    incpid->last_error = incpid->error;

    incpid->IncPID_Output += (p_term + i_term + d_term);

    // PID����޷�
    if (incpid->IncPID_Output > incpid->maxOutput)
        incpid->IncPID_Output = incpid->maxOutput;
    else if (incpid->IncPID_Output < incpid->minOutput)
        incpid->IncPID_Output = incpid->minOutput;

    return incpid->IncPID_Output;
}

/**
 * @brief  ָ����Ȩ�ƶ�ƽ���˲�
 * @param  input ����ֵ
 * @param  filtered_value �ϴ��˲����ֵ
 * @param  alpha �˲�ϵ��
 * @retval �˲�����
 */
float EWMA_filter(float input, float filtered_value, float alpha)
{
    return alpha * input + (1.0 - alpha) * filtered_value;
}