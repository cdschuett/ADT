#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <stdbool.h>
#include <unistd.h>
#include <time.h>

bool initial = true;

int menuOption = 0;
int menuChoice = 0;
pid_t eicas_pid = -1;
pid_t test_pid = -1;

void log_message(const char* message)
{
    FILE *log_file = fopen("/home/pi/logs/mx_application.log", "a");
    
    if (log_file == NULL)
    {
        perror("Error opening log file");
        return;
    }
    
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    char time_str[20];
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", t);
    
    fprintf(log_file, "[%s] %s\n", time_str, message);
    
    fflush(log_file);
    
    fclose(log_file);
}

void start_eicas()
{
    eicas_pid = fork();
    if (eicas_pid == -1)
    {
        log_message("EICAS process start failure.");
        exit(EXIT_FAILURE);
    }
    else if (eicas_pid == 0)
    {
        execlp("python", "python", "/home/pi/Documents/py_test/ADT/eicas.py", (char *) NULL);
        log_message("EICAS execution failure.");
        exit(EXIT_FAILURE);
    }
    else
    {
        char buffer[100];
        snprintf(buffer, sizeof(buffer), "EICAS started with PID: %d\n", eicas_pid);
        log_message(buffer); 
    }
}

void stop_eicas()
{
    if (eicas_pid != 0)
    {
        if (kill(eicas_pid, SIGTERM) == 0)
        {
            log_message("EICAS exited.");
        }
        else
        {
            log_message("EICAS termination failed."); 
        }
    }
    else
    {
        log_message("EICAS not running.");
    }
}

void start_test()
{
    test_pid = fork();
    if (test_pid == -1)
    {
        log_message("Test pattern process start failure.");
        exit(EXIT_FAILURE);
    }
    else if (test_pid == 0)
    {
        execlp("python", "python", "/home/pi/Documents/py_test/ADT/test_pattern.py", (char *) NULL);
        log_message("Test pattern execution failure.");
        exit(EXIT_FAILURE);
    }
    else
    {
        char buffer[100];
        snprintf(buffer, sizeof(buffer), "Test pattern started with PID: %d\n", test_pid);
        log_message(buffer); 
    }
}

void stop_test()
{
    if (test_pid != 0)
    {
        if (kill(test_pid, SIGTERM) == 0)
        {
            log_message("Test exited.");
        }
        else
        {
            log_message("Test termination failed."); 
        }
    }
    else
    {
        log_message("Test not running.");
    }
}



int choice()
{
    int num;
    int result = 0;
    do
    {
        num = 0;
        result = scanf("%d", &num);
        printf("%d %d ", result, num);
    } while ( result != 1);
    return num;
}

int menuDisplay(int screen)
{
    switch(screen)
    {
        case 0:
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("RUNNING: \t\t\tEICAS                           ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("DISABLE EICAS\t\t(1)                           ");
            puts("TEST PATTERN\t\t(2)                            ");
            puts("SOFTWARE PART VERIFICATION\t(3)                ");
            puts("SOFTWARE PART UPDATE\t      (4)                ");
            puts("SOFTWARE PART MANIFEST\t    (5)                ");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 1:
            stop_eicas();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("DISABLING: \t\t\tEICAS                         ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("START EICAS\t\t(6)                             ");
            puts("TEST PATTERN\t\t(2)                            ");
            puts("SOFTWARE PART VERIFICATION\t(3)                ");
            puts("SOFTWARE PART UPDATE\t      (4)                ");
            puts("SOFTWARE PART MANIFEST\t    (5)                ");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 2:
            start_test();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("DISABLING: \t\t\tEICAS                         ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("START EICAS\t\t(6)                             ");
            puts("TEST PATTERN\t\t(2)                            ");
            puts("SOFTWARE PART VERIFICATION\t(3)                ");
            puts("SOFTWARE PART UPDATE\t      (4)                ");
            puts("SOFTWARE PART MANIFEST\t    (5)                ");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
    }
}

int main()
{
    do
    {
        if (initial)
        {
            start_eicas();
            menuChoice = 0;
            initial = false;
            system("clear");

        }
        else
        {
            menuChoice = choice();
            system("clear");
        }
        menuDisplay(menuChoice);
    } while( true );
    
    return(0);
}