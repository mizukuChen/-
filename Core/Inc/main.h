/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32h7xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "tim.h"
#include "usart.h"
#include "gpio.h"

#include <stdio.h>
#include "math.h"
#include "stdlib.h"
#include "string.h"
#include "stdbool.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define KEY1_Pin GPIO_PIN_3
#define KEY1_GPIO_Port GPIOE
#define PWM_DUO_Pin GPIO_PIN_5
#define PWM_DUO_GPIO_Port GPIOA
#define OLED_D0_Pin GPIO_PIN_4
#define OLED_D0_GPIO_Port GPIOC
#define KEY2_Pin GPIO_PIN_5
#define KEY2_GPIO_Port GPIOC
#define OLED_D1_Pin GPIO_PIN_0
#define OLED_D1_GPIO_Port GPIOB
#define OLED_RES_Pin GPIO_PIN_1
#define OLED_RES_GPIO_Port GPIOB
#define OLED_DC_Pin GPIO_PIN_2
#define OLED_DC_GPIO_Port GPIOB
#define OLED_CS_Pin GPIO_PIN_7
#define OLED_CS_GPIO_Port GPIOE
#define DirY_Pin GPIO_PIN_8
#define DirY_GPIO_Port GPIOC
#define DirX_Pin GPIO_PIN_9
#define DirX_GPIO_Port GPIOC
#define StpY_Pin GPIO_PIN_8
#define StpY_GPIO_Port GPIOA
#define StpX_Pin GPIO_PIN_9
#define StpX_GPIO_Port GPIOA
#define EnY_Pin GPIO_PIN_10
#define EnY_GPIO_Port GPIOA
#define EnX_Pin GPIO_PIN_11
#define EnX_GPIO_Port GPIOA
#define YIN1_Pin GPIO_PIN_12
#define YIN1_GPIO_Port GPIOC
#define YIN2_Pin GPIO_PIN_1
#define YIN2_GPIO_Port GPIOD
#define YIN3_Pin GPIO_PIN_3
#define YIN3_GPIO_Port GPIOD
#define YIN4_Pin GPIO_PIN_5
#define YIN4_GPIO_Port GPIOD
#define XIN2_Pin GPIO_PIN_7
#define XIN2_GPIO_Port GPIOD
#define XIN1_Pin GPIO_PIN_3
#define XIN1_GPIO_Port GPIOB
#define XIN3_Pin GPIO_PIN_4
#define XIN3_GPIO_Port GPIOB
#define XIN4_Pin GPIO_PIN_5
#define XIN4_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
