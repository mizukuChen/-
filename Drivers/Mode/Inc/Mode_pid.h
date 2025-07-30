/**
 * @file    PID.h
 * @version v1.3
 * @author  Bairu
 * @date    2024��8��21�� 16:09:44
 * @brief   PID�㷨ͷ�ļ�������PID�����ṹ�弰����
 */

#ifndef __MODE_PID_H
#define __MODE_PID_H

#include "stdint.h"

#define K_p 1
#define K_i 2
#define K_d 3

/**
 * PID�����ø�����
 * 1��P������Ӧ�ٶȺ����ȣ���С��Ӧ�������������񵴣���I��D�Ļ�����
 * 2��I����ϵͳ������������ʱ����ƫ���߾��ȣ�ͬʱҲ��������Ӧ�ٶȣ��������壬���������񵴡�
 * 3��D���ƹ�����񵴣���Сϵͳ����壬����������Ӧ�ٶȡ�D������һ�������ǵֿ�����ͻ�����ţ���ֹϵͳ��ͻ�䡣
 */

/**************************** λ��ʽPID ****************************/

typedef struct
{
    float Kp, Ki, Kd;               // ���������֡�΢��ϵ��
    float target;                   // Ŀ��ֵ
    float error;                    // ƫ��ֵ
    float last_error;               // ǰһ��ƫ��
    float integral;                 // ����ֵ
    float maxIntegral, minIntegral; // �����޷�
    float maxOutput, minOutput;     // ����޷�
} PID;

void PID_Init(PID *pid, float Kp, float Ki, float Kd, float target,
              float minIntegral, float maxIntegral,
              float minOutput, float maxOutput);
void PID_ResetTarget(PID *pid, float target);
void PID_Reset_pid(PID *pid, uint8_t Kx, float coefficient);
float PID_Compute(PID *pid, float input);
float PID_Compute_reverse(PID *pid, float input, float Kp);

/******************************************************************/

/**************************** ����ʽPID ****************************/

typedef struct
{
    float Kp, Ki, Kd;           // ���������֡�΢��ϵ��
    float target;               // Ŀ��ֵ
    float error;                // ƫ��ֵ
    float last_error;           // ǰһ��ƫ��
    float prev_error;           // ǰ����ƫ��
    float maxOutput, minOutput; // ����޷�
    float IncPID_Output;        // PID������
} IncPID;

void IncPID_Init(IncPID *incpid, float Kp, float Ki, float Kd, float target,
                 float minOutput, float maxOutput);
void IncPID_ResetTarget(IncPID *incpid, float target);
void IncPID_Reset_pid(IncPID *incpid, uint8_t Kx, float coefficient);
float IncPID_Compute(IncPID *incpid, float input);

/******************************************************************/

/***************************** �˲��� *****************************/

float EWMA_filter(float input, float filtered_value, float alpha);

/******************************************************************/

#endif /* __PID_H */