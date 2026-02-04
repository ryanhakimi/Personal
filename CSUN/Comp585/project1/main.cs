using System;

class CalculatorApp
{
    static void Main()
    {
        PrintInterface();
    }
    
    static void PrintInterface()
    {
        // print menu
        Console.WriteLine();
        Console.WriteLine("""

        |========================================|
        |         Welcome the Calculator         |
        |========================================|
        |   1. Add Operation                     |
        |   2. Subtract Operation                |
        |   3. Multiply Operation                |
        |   4. Divide Operation                  |
        |   5. Modulus                           |
        |   6. Square Root                       |
        |   7. Square                            |
        |   8. Reciprocal                        |
        |   9. Exit                              |
        |========================================|

        """);

        // read user selection
        Console.WriteLine("Select an operation:");
        if (!int.TryParse(Console.ReadLine(), out int selection)) return;

        // call guide func
        GuideUser(selection);
    }

    static void GuideUser(int selection)
    {
        double result = 0;
        switch (selection)
        {
            default:
            Console.WriteLine("\nInvalid selection.");
            PrintInterface();
            break;

            case >= 1 and <= 5:
                Console.WriteLine("\nEnter the first number:");
                if (!double.TryParse(Console.ReadLine(), out double num1)) return;
                Console.WriteLine("\nEnter the second number:");
                if (!double.TryParse(Console.ReadLine(), out double num2)) return;
                
                if (selection == 1) result = Add(num1, num2);
                else if (selection == 2) result = Subtract(num1, num2);
                else if (selection == 3) result = Multiply(num1, num2);
                else if (selection == 4) result = Divide(num1, num2);
                else if (selection == 5) result = Modulus(num1, num2);
                Console.WriteLine($"\nResult:\n{result}");
                PrintInterface();
                break;

            case 6:
            case 7:
            case 8:
                Console.WriteLine("\nEnter a number:");
                if (!double.TryParse(Console.ReadLine(), out double num)) return;

                if (selection == 6) result = SquareRoot(num);
                else if (selection == 7) result = Square(num);
                else if (selection == 8) result = Reciprocal(num);
                Console.WriteLine($"\nResult:\n{result}");
                PrintInterface();
                break;

            case 9:
                Exit();
                break;
        }
    }

    // selection 1
    static double Add(double num1, double num2)
    {
        return num1 + num2;
    }

    // selection 2
    static double Subtract(double num1, double num2)
    {
        return num1 - num2;
    }

    // selection 3
    static double Multiply(double num1, double num2)
    {
        return num1 * num2;
    }

    // selection 4
    static double Divide(double num1, double num2)
    {
        return num1 / num2;
    }

    // selection 5
    static double Modulus(double num1, double num2)
    {
        return num1 % num2;
    }

    // selection 6
    static double SquareRoot(double num)
    {
        return Math.Sqrt(num);
    }

    // selection 7
    static double Square(double num)
    {
        return num * num;
    }

    // selection 8
    static double Reciprocal(double num)
    {
        return 1 / num;
    }

    // selection 9
    static void Exit()
    {
        Console.WriteLine("\nExiting now...\n\n");
        Environment.Exit(0);
    }
}