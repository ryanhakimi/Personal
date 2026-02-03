using System;
using System.IO;

int selection;

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
        |   5. Modulus                           |\n
        |   6. Square Root                       |\n
        |   7. Square                            |\n
        |   8. Reciprocal                        |\n
        |   9. Exit                              |\n
        |========================================|\n"
    );

    // read user selection
    Console.WriteLine("\nSelect an operation: ");
    int selection = Console.ReadLine();
};

static void guideUser(int selection)
{
    switch(selection)
    {
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
            Console.WriteLine("\nEnter the first number: ");
            double num1 = Console.ReadLine();
            Console.WriteLine("\nEnter the second number: ");
            double num2 = Console.ReadLine();
            break;
        case 6:
        case 7:
        case 8:
            Console.WriteLine("\nEnter a number: ");
            double num = Console.ReadLine();
        case 9:
            exit();
    };
};

// selection 1
double add(double num1, double num2)
{
    return num1 + num2;
};

// selection 2
double subract(double num1, double num2)
{
    return num1 - num2;
};

// selection 3
double multiply(double num1, double num2)
{
    return num1 * num2;
};

// selection 4
double divide(double num1, double num2)
{
    return num1 / num2;
};

// selection 5
double modulus(double num1, double num2)
{
    return num1 % num2;
};

// selection 6
double squareRoot(double num)
{
    return;
};

// selection 7
double square(double num)
{
    return;
};

// selection 8
double reciprocal(double num)
{
    return;
};

// selection 9
static void exit()
{
    Console.WriteLine("\n\nExiting now...");
    Environment.Exit(0);
};