// UI模组

#include <main.h>
#include <Mode_UI.h>

volatile bool key1state;
volatile bool key2state;

void UI_Control(void)
{
    key1state = 0;
    key2state = 0;
    uint8_t choice = 1;
    uint8_t select = 0;
    //uint8_t name[SUPER_NUMBER][SUPER_TASK_NUMBER];
    //uint16_t value[SUPER_NUMBER][SUPER_TASK_NUMBER];
    //for(int i = 0; i < SUPER_NUMBER; i++)
    //{
    //    name[i][0] = 0;
    //}
    while (1)
    {
        if (select != 1)
        {
            OLED_ShowString(0, 0, "Please select the", 8, 1);
            OLED_ShowString(0, 10, "task:", 8, 1);
            OLED_ShowString(0, 20, "Config", 8, 1);
            OLED_ShowString(0, 30, "Task 1", 8, 1);
            OLED_ShowString(0, 40, "Task 2", 8, 1);
            OLED_ShowString(0, 50, "Task 3", 8, 1);
            OLED_ShowString(64, 20, "Task 4", 8, 1);
            OLED_ShowString(64, 30, "further", 8, 1);
            OLED_ShowString(64, 40, "superUI", 8, 1);
            if (key1state == 1)
            {
                if (choice != 7)
                    choice += 1;
                else
                    choice = 1;
                key1state = 0;
            }
            switch (choice)
            {
            case 1:
                OLED_ShowString(0, 20, "Config", 8, 0);
                break;
            case 2:
                OLED_ShowString(0, 30, "Task 1", 8, 0);
                break;
            case 3:
                OLED_ShowString(0, 40, "Task 2", 8, 0);
                break;
            case 4:
                OLED_ShowString(0, 50, "Task 3", 8, 0);
                break;
            case 5:
                OLED_ShowString(64, 20, "Task 4", 8, 0);
                break;
            case 6:
                OLED_ShowString(64, 30, "further", 8, 0);
                break;
            case 7:
                OLED_ShowString(64, 40, "superUI", 8, 0);
                break;
            default:
                break;
            }
            OLED_Refresh();
        }
        if (key2state == 1)
        {
            select = 1;
            key2state = 0;
            OLED_Clear();
            if (choice == 6)
            {
                OLED_ShowString(0, 10, "Further Mode", 8, 1);
                OLED_ShowString(0, 20, "Please wait...", 8, 1);
                OLED_Refresh();
                further();
                break;
            }
            if (choice == 1)
            {
                OLED_ShowString(0, 10, "Config Mode", 8, 1);
                OLED_ShowString(0, 20, "Please wait...", 8, 1);
                OLED_Refresh();
                config();
                break;
            }
            if (choice == 7)
            {
                OLED_ShowString(0, 10, "Config Mode", 8, 1);
                OLED_ShowString(0, 20, "Please wait...", 8, 1);
                OLED_Refresh();
                //superUI(name,value);
                break;
            }
            OLED_ShowString(0, 10, "The task will start", 8, 1);
            OLED_ShowString(0, 20, "in 3 seconds.", 8, 1);
            OLED_Refresh();
            //HAL_Delay(3000);
            OLED_Clear();
            OLED_ShowString(0, 10, "The task is running.", 8, 1);
            OLED_Refresh();
            switch (choice)
            {
            case 2:
                task1();
                break;
            case 3:
                task2();
                break;
            case 4:
                task3();
                break;
            case 5:
                task4();
                break;
            default:
                break;
            }
            OLED_Clear();
            OLED_ShowString(0, 10, "Task Done.", 8, 1);
            OLED_ShowString(0, 20, "Will return", 8, 1);
            OLED_ShowString(0, 30, "in 3 seconds.", 8, 1);
            OLED_Refresh();
            HAL_Delay(3000);
            OLED_Clear();
            select = 0;
            choice = 1;
        }
    }
}

void further(void)
{
    OLED_Clear();
    uint8_t choice = 1;
    uint8_t select = 0;
    while (1)
    {
        if (select != 1)
        {
            OLED_ShowString(0, 0, "Please select the", 8, 1);
            OLED_ShowString(0, 10, "task:", 8, 1);
            OLED_ShowString(0, 20, "Further 1", 8, 1);
            OLED_ShowString(0, 30, "Further 2", 8, 1);
            OLED_ShowString(0, 40, "Further 3", 8, 1);
            OLED_ShowString(0, 50, "Further 4", 8, 1);
            OLED_ShowString(64, 20, "back", 8, 1);
            if (key1state == 1)
            {
                if (choice != 5)
                    choice += 1;
                else
                    choice = 1;
                key1state = 0;
            }
            switch (choice)
            {
            case 1:
                OLED_ShowString(0, 20, "Further 1", 8, 0);
                break;
            case 2:
                OLED_ShowString(0, 30, "Further 2", 8, 0);
                break;
            case 3:
                OLED_ShowString(0, 40, "Further 3", 8, 0);
                break;
            case 4:
                OLED_ShowString(0, 50, "Further 4", 8, 0);
                break;
            case 5:
                OLED_ShowString(64, 20, "back", 8, 0);
                break;
            default:
                break;
            }
            OLED_Refresh();
        }
        if (key2state == 1)
        {
            select = 1;
            key2state = 0;
            OLED_Clear();
            if(choice == 5)
            {
                return; // back to main menu
            }
            OLED_ShowString(0, 10, "The task will start", 8, 1);
            OLED_ShowString(0, 20, "in 3 seconds.", 8, 1);
            OLED_Refresh();
            //HAL_Delay(3000);
            OLED_Clear();
            OLED_ShowString(0, 10, "The task is running.", 8, 1);
            OLED_Refresh();
            switch (choice)
            {
            case 1:
                further_task1();
                break;
            case 2:
                further_task2();
                break;
            case 3:
                further_task3();
                break;
            case 4:
                further_task4();
            default:
                break;
            }
            OLED_Clear();
            OLED_ShowString(0, 10, "Task Done.", 8, 1);
            OLED_ShowString(0, 20, "Will return", 8, 1);
            OLED_ShowString(0, 30, "in 3 seconds.", 8, 1);
            OLED_Refresh();
            //HAL_Delay(3000);
            OLED_Clear();
            select = 0;
            choice = 1;
        }
    }
}

void config(void)
{
    OLED_Clear();
    uint8_t choice = 1;
    uint8_t select = 0;
    while (1)
    {
        if (select != 1)
        {
            OLED_ShowString(0, 0, "Please select", 8, 1);
            OLED_ShowString(0, 10, "config 1", 8, 1);
            OLED_ShowString(0, 20, "config 2", 8, 1);
            OLED_ShowString(0, 30, "config 3", 8, 1);
            OLED_ShowString(0, 40, "config 4", 8, 1);
            OLED_ShowString(0, 50, "config 5", 8, 1);
            OLED_ShowString(64, 10, "config 6", 8, 1);
            OLED_ShowString(64, 20, "config 7", 8, 1);
            OLED_ShowString(64, 30, "config 8", 8, 1);
            OLED_ShowString(64, 40, "config 9", 8, 1);
            OLED_ShowString(64, 50, "back", 8, 1);
            if (key1state == 1)
            {
                if (choice != 10)
                    choice += 1;
                else
                    choice = 1;
                key1state = 0;
            }
            switch (choice)
            {
            case 1:
                OLED_ShowString(0, 10, "config 1", 8, 0);
                break;
            case 2:
                OLED_ShowString(0, 20, "config 2", 8, 0);
                break;
            case 3:
                OLED_ShowString(0, 30, "config 3", 8, 0);
                break;
            case 4:
                OLED_ShowString(0, 40, "config 4", 8, 0);
                break;
            case 5:
                OLED_ShowString(0, 50, "config 5", 8, 0);
                break;
            case 6:
                OLED_ShowString(64, 10, "config 6", 8, 0);
                break;
            case 7:
                OLED_ShowString(64, 20, "config 7", 8, 0);
                break;
            case 8:
                OLED_ShowString(64, 30, "config 8", 8, 0);
                break;
            case 9:
                OLED_ShowString(64, 40, "config 9", 8, 0);
                break;
            case 10:
                OLED_ShowString(64, 50, "back", 8, 0);
                break;
            default:
                break;
            }
            OLED_Refresh();
        }
        if (key2state == 1)
        {
            select = 1;
            key2state = 0;
            OLED_Clear();
            if(choice == 10)
            {
                return; // back to main menu
            }
            //OLED_ShowString(0, 10, "The task will start", 8, 1);
            //OLED_ShowString(0, 20, "in 3 seconds.", 8, 1);
            //OLED_Refresh();
            //HAL_Delay(3000);
            //OLED_Clear();
            //OLED_ShowString(0, 10, "The task is running.", 8, 1);
            //OLED_Refresh();
            switch (choice)
            {
            case 1:
                config1();
                break;
            case 2:
                config2();
                break;
            case 3:
                config3();
                break;
            case 4:
                config4();
                break;
            case 5:
                config5();
                break;
            case 6:
                config6();
                break;
            case 7:
                config7();
                break;
            case 8:
                config8();
                break;
            case 9:
                config9();
                break;
            default:
                break;
            }
            OLED_Clear();
            OLED_ShowString(0, 10, "Task Done.", 8, 1);
            OLED_ShowString(0, 20, "Will return", 8, 1);
            OLED_ShowString(0, 30, "in 3 seconds.", 8, 1);
            OLED_Refresh();
            HAL_Delay(1000);
            OLED_Clear();
            select = 0;
            choice = 1;
        }
    }
}


