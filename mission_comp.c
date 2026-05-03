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
pid_t stop_eicas_pid = -1;
pid_t stop_test_pid = -1;

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
    system("/home/pi/Documents/py_test/ADT/start.sh");
    log_message("EICAS execution start.");
}

void stop_eicas()
{
    system("/home/pi/Documents/py_test/ADT/stop_eicas.sh");
    log_message("EICAS execution stop.");
}

void start_test()
{
    system("/home/pi/Documents/py_test/ADT/test.sh");
    log_message("TEST execution start.");
}

void stop_test()
{
    system("/home/pi/Documents/py_test/ADT/stop_test.sh");
    log_message("TEST execution start.");
}

void verification()
{
    system("/home/pi/Documents/py_test/ADT/verify.sh");
    log_message("Part verification executed.");

    char line[1000];
    FILE *fptr = fopen("/home/pi/Documents/py_test/ADT/verification_results.txt", "r");
    
    if (fptr == NULL)
    {
        perror("Error opening results file");
        return;
    }
    printf("\n---Contents of Verification---\n");
    while (fgets(line, sizeof(line), fptr) != NULL)
    {
        printf("%s", line);
    }
    printf("------------------------------\n");
    printf("Press a key to continue...\n");
    getchar();
    getchar();

    fclose(fptr);
    system("clear");
    return;
}


/*
 * Keeping for reference
void stop_test()
{
    stop_test_pid = fork();
    if (stop_test_pid == -1)
    {
        log_message("TEST process stop failure.");
        exit(EXIT_FAILURE);
    }
    else if (eicas_pid == 0)
    {
        //execlp("python", "python", "/home/pi/Documents/py_test/ADT/eicas.py", (char *) NULL);
        execlp("/home/pi/Documents/py_test/ADT/stop_test.sh", "/home/pi/Documents/py_test/ADT/stop_test.sh", (char *) NULL);
        log_message("TEST termination failure.");
        exit(EXIT_FAILURE);
    }
    else
    {
        char buffer[100];
        snprintf(buffer, sizeof(buffer), "TEST stopped with PID: %d\n", stop_eicas_pid);
        log_message(buffer); 
    }
}
*/


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
            system("clear");
            start_eicas();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("RUNNING: \t\t\tEICAS                           ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("DISABLE EICAS\t\t\t(1)");
            puts("TEST PATTERN\t\t\t(2)");
            puts("SOFTWARE PART VERIFICATION\t(3)");
            puts("SOFTWARE PART UPDATE\t\t(4)");
            puts("SOFTWARE PART MANIFEST\t\t(5)");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 1:
            system("clear");
            stop_eicas();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("DISABLING: \t\t\tEICAS                         ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("START EICAS\t\t\t(6)");
            puts("TEST PATTERN\t\t\t(2)");
            puts("SOFTWARE PART VERIFICATION\t(3)");
            puts("SOFTWARE PART UPDATE\t\t(4)");
            puts("SOFTWARE PART MANIFEST\t\t(5)");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 2:
            system("clear");
            start_test();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("DISABLING: \t\t\tEICAS                         ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("START EICAS\t\t\t(6)");
            puts("STOP TEST PATTERN\t\t(7)");
            puts("SOFTWARE PART VERIFICATION\t(3)");
            puts("SOFTWARE PART UPDATE\t\t(4)");
            puts("SOFTWARE PART MANIFEST\t\t(5)");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 3:
            system("clear");
            verification();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("RETURN TO MAIN MENU\t(0)");
            puts("SOFTWARE PART UPDATE\t(4)");
            puts("SOFTWARE PART MANIFEST\t(5)");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 6:
            system("clear");
            start_eicas();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("STARTING: \t\t\tEICAS                          ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("STOP EICAS\t\t(1)                             ");
            puts("TEST PATTERN\t\t(2)                            ");
            puts("SOFTWARE PART VERIFICATION\t(3)                ");
            puts("SOFTWARE PART UPDATE\t      (4)                ");
            puts("SOFTWARE PART MANIFEST\t    (5)                ");
            putchar(10);
            menuOption = puts("SELECT YOUR OPTION: ");
            break;
        case 7:
            system("clear");
            stop_test();
            puts("===============================================");
            puts("              MAINTENANCE DISPLAY              ");
            puts("===============================================");
            puts("STARTING: \t\t\tEICAS                          ");
            puts("REGISTRATION NUMBER: \t\tN1337                 ");
            putchar(10);
            putchar(10);
            puts("START EICAS\t\t(1)                             ");
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
            //start_eicas();
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
