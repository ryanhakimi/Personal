using System;
using System.IO;

// global vars
int selection;
int num1;
int num2;

static void printInterface()
{
    // print menu
    Console.WriteLine(
        @"\n|========================================|\n
        |       Welcome to Basic Calculator       |\n
        |========================================|\n
        |   1. Add Operation                     |\n
        |   2. Subtract Operation                |\n
        |   3. Multiply Operation                |\n
        |   4. Divide Operation                  |\n
        |   5. Exit                              |\n
        |========================================|\n"
    );

    // read user selection
    Console.WriteLine("\nSelect an operation: ");
    int selection = Console.ReadLine();

    // read user nums
    Console.WriteLine("\n\nEnter the first number: ");
    int num1 = Console.ReadLine();
    Console.WriteLine("\n\nEnter the second number: ");
    int num2 = Console.ReadLine();
}

